from datetime import date, timedelta
from calendar import monthrange
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.db import transaction, IntegrityError
from .models import Auditoria, ConceptoCobro, DetallePago, Matricula, Obligacion, Pago

def auditar(usuario, modulo, accion, objeto, descripcion):
    Auditoria.objects.create(usuario=usuario,modulo=modulo,accion=accion,registro=str(objeto.pk),descripcion=descripcion)

def add_months(start, n):
    y=start.year+(start.month-1+n)//12; m=(start.month-1+n)%12+1
    return date(y,m,min(start.day,monthrange(y,m)[1]))

@transaction.atomic
def crear_matricula(form, usuario):
    m=form.save(commit=False)
    m.full_clean(exclude=['numero'])
    m.numero='TEMP-'+__import__('uuid').uuid4().hex
    m.save()
    m.numero=f'MAT-{m.periodo_id}-{m.pk:06d}'
    m.save(update_fields=['numero'])
    concepto=ConceptoCobro.objects.filter(tipo='MATRICULA',activo=True).first()
    if not concepto: raise ValidationError('Configure un concepto de matrícula activo antes de matricular.')
    Obligacion.objects.create(matricula=m,concepto=concepto,descripcion='Derecho de matrícula',valor=m.valor_matricula-m.descuento,vencimiento=m.fecha)
    pension=ConceptoCobro.objects.filter(tipo='PENSION',activo=True).first()
    if pension:
        for n in range(10):
            vencimiento=add_months(m.periodo.fecha_inicio,n)
            if vencimiento>m.periodo.fecha_fin: break
            Obligacion.objects.create(matricula=m,concepto=pension,descripcion=f'Pensión {vencimiento:%Y-%m}',valor=pension.valor_base,vencimiento=vencimiento)
    auditar(usuario,'Matrículas','CREAR',m,f'Matrícula {m.numero} creada y obligaciones generadas')
    return m

@transaction.atomic
def registrar_pago(obligacion_id,valor,referencia,usuario):
    oblig=Obligacion.objects.select_for_update().get(pk=obligacion_id)
    if oblig.anulada or oblig.matricula.estado=='Cancelada': raise ValidationError('Obligación no pagable.')
    saldo=oblig.saldo
    if valor<=0 or valor>saldo: raise ValidationError(f'El abono debe ser mayor que cero y no superar el saldo (${saldo}).')
    if Pago.objects.filter(referencia=referencia).exists(): raise ValidationError('La referencia ya existe.')
    pago=Pago.objects.create(referencia=referencia,total=valor,registrado_por=usuario)
    DetallePago.objects.create(pago=pago,obligacion=oblig,valor=valor)
    auditar(usuario,'Pagos','CREAR',pago,f'Pago {referencia} de ${valor} a obligación {oblig.pk}')
    return pago

@transaction.atomic
def anular_pago(pago_id,justificacion,usuario):
    pago=Pago.objects.select_for_update().get(pk=pago_id)
    if pago.estado!='Confirmado': raise ValidationError('El pago ya está anulado.')
    if len(justificacion.strip())<8: raise ValidationError('Justificación insuficiente.')
    pago.estado='Anulado'; pago.motivo_anulacion=justificacion; pago.anulado_por=usuario
    pago.save(update_fields=['estado','motivo_anulacion','anulado_por'])
    auditar(usuario,'Pagos','ANULAR',pago,f'Anulación pago {pago.referencia}: {justificacion}')
    return pago
