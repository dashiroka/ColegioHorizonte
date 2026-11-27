from decimal import Decimal
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Sum
from django.utils import timezone

class Estudiante(models.Model):
    TIPOS=[('TI','Tarjeta de identidad'),('CC','Cédula'),('CE','Cédula extranjería'),('RC','Registro civil')]
    tipo_documento=models.CharField(max_length=3, choices=TIPOS)
    documento=models.CharField(max_length=25)
    nombres=models.CharField(max_length=100)
    apellidos=models.CharField(max_length=100)
    fecha_nacimiento=models.DateField()
    direccion=models.CharField(max_length=200)
    telefono=models.CharField(max_length=25)
    correo=models.EmailField(blank=True)
    estado=models.CharField(max_length=12, choices=[('Activo','Activo'),('Inactivo','Inactivo'),('Retirado','Retirado')], default='Activo')
    class Meta:
        constraints=[models.UniqueConstraint(fields=['tipo_documento','documento'],name='uq_estudiante_documento')]
        ordering=['apellidos','nombres']
    def __str__(self): return f'{self.nombres} {self.apellidos} ({self.documento})'

class Acudiente(models.Model):
    documento=models.CharField(max_length=25,unique=True)
    nombres=models.CharField(max_length=100)
    apellidos=models.CharField(max_length=100)
    telefono=models.CharField(max_length=25)
    correo=models.EmailField(blank=True)
    activo=models.BooleanField(default=True)
    def __str__(self): return f'{self.nombres} {self.apellidos}'

class EstudianteAcudiente(models.Model):
    estudiante=models.ForeignKey(Estudiante,on_delete=models.PROTECT)
    acudiente=models.ForeignKey(Acudiente,on_delete=models.PROTECT)
    parentesco=models.CharField(max_length=40)
    responsable_pago=models.BooleanField(default=False)
    class Meta:
        constraints=[models.UniqueConstraint(fields=['estudiante','acudiente'],name='uq_est_acudiente')]

class Grado(models.Model):
    nombre=models.CharField(max_length=30,unique=True)
    activo=models.BooleanField(default=True)
    def __str__(self): return self.nombre

class Grupo(models.Model):
    grado=models.ForeignKey(Grado,on_delete=models.PROTECT)
    nombre=models.CharField(max_length=30)
    jornada=models.CharField(max_length=20,choices=[('Mañana','Mañana'),('Tarde','Tarde')])
    activo=models.BooleanField(default=True)
    class Meta:
        constraints=[models.UniqueConstraint(fields=['grado','nombre','jornada'],name='uq_grupo')]
    def __str__(self): return f'{self.grado} - {self.nombre} ({self.jornada})'

class PeriodoAcademico(models.Model):
    nombre=models.CharField(max_length=50,unique=True)
    fecha_inicio=models.DateField()
    fecha_fin=models.DateField()
    activo=models.BooleanField(default=True)
    def clean(self):
        if self.fecha_inicio and self.fecha_fin and self.fecha_fin < self.fecha_inicio: raise ValidationError('El fin debe ser posterior al inicio.')
    def __str__(self): return self.nombre

class ConceptoCobro(models.Model):
    TIPOS=[('MATRICULA','Matrícula'),('PENSION','Pensión'),('OTRO','Otro')]
    nombre=models.CharField(max_length=80,unique=True)
    tipo=models.CharField(max_length=12,choices=TIPOS)
    valor_base=models.DecimalField(max_digits=12,decimal_places=2)
    activo=models.BooleanField(default=True)
    def __str__(self): return self.nombre

class Matricula(models.Model):
    estudiante=models.ForeignKey(Estudiante,on_delete=models.PROTECT)
    grupo=models.ForeignKey(Grupo,on_delete=models.PROTECT)
    periodo=models.ForeignKey(PeriodoAcademico,on_delete=models.PROTECT)
    numero=models.CharField(max_length=40,unique=True,editable=False)
    fecha=models.DateField(default=timezone.localdate)
    valor_matricula=models.DecimalField(max_digits=12,decimal_places=2,default=Decimal('0.00'))
    descuento=models.DecimalField(max_digits=12,decimal_places=2,default=Decimal('0.00'))
    estado=models.CharField(max_length=12,choices=[('Activa','Activa'),('Pendiente','Pendiente'),('Cancelada','Cancelada'),('Finalizada','Finalizada')],default='Activa')
    class Meta:
        constraints=[models.UniqueConstraint(fields=['estudiante','periodo'],name='uq_matricula_estudiante_periodo')]
    def clean(self):
        if self.estudiante_id and self.estudiante.estado!='Activo': raise ValidationError('El estudiante debe estar activo.')
        if self.grupo_id and (not self.grupo.activo or not self.grupo.grado.activo): raise ValidationError('El grupo y grado deben estar activos.')
        if self.periodo_id and not self.periodo.activo: raise ValidationError('El período debe estar activo.')
        if self.descuento < 0 or self.valor_matricula < 0 or self.descuento > self.valor_matricula: raise ValidationError('Valores de matrícula o descuento inválidos.')
    def __str__(self): return self.numero

class Obligacion(models.Model):
    matricula=models.ForeignKey(Matricula,on_delete=models.PROTECT,related_name='obligaciones')
    concepto=models.ForeignKey(ConceptoCobro,on_delete=models.PROTECT)
    descripcion=models.CharField(max_length=100)
    valor=models.DecimalField(max_digits=12,decimal_places=2)
    vencimiento=models.DateField()
    anulada=models.BooleanField(default=False)
    def abonado(self):
        return self.detalles.filter(pago__estado='Confirmado').aggregate(t=Sum('valor'))['t'] or Decimal('0.00')
    @property
    def saldo(self): return self.valor-self.abonado()
    @property
    def estado(self):
        if self.anulada: return 'Anulado'
        if self.saldo <= 0: return 'Pagado'
        if self.abonado() > 0: return 'Pago parcial'
        if self.vencimiento < timezone.localdate(): return 'Vencido'
        return 'Pendiente'
    def __str__(self): return f'{self.descripcion} - {self.matricula.numero}'

class Pago(models.Model):
    referencia=models.CharField(max_length=45,unique=True)
    fecha=models.DateTimeField(default=timezone.now)
    registrado_por=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT)
    total=models.DecimalField(max_digits=12,decimal_places=2)
    estado=models.CharField(max_length=12,choices=[('Confirmado','Confirmado'),('Anulado','Anulado')],default='Confirmado')
    motivo_anulacion=models.TextField(blank=True)
    anulado_por=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,null=True,blank=True,related_name='pagos_anulados')
    def __str__(self): return self.referencia

class DetallePago(models.Model):
    pago=models.ForeignKey(Pago,on_delete=models.PROTECT,related_name='detalles')
    obligacion=models.ForeignKey(Obligacion,on_delete=models.PROTECT,related_name='detalles')
    valor=models.DecimalField(max_digits=12,decimal_places=2)
    class Meta:
        constraints=[models.UniqueConstraint(fields=['pago','obligacion'],name='uq_detalle_pago')]

class Auditoria(models.Model):
    usuario=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True)
    fecha=models.DateTimeField(auto_now_add=True)
    modulo=models.CharField(max_length=50)
    accion=models.CharField(max_length=40)
    registro=models.CharField(max_length=50)
    descripcion=models.TextField()
    class Meta: ordering=['-fecha']
