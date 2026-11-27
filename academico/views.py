from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404,redirect,render
from django.views.decorators.http import require_http_methods
from .forms import (EstudianteForm, AcudienteForm, EstudianteAcudienteForm, GrupoForm, PeriodoForm,
                    ConceptoForm,MatriculaForm,PagoForm,AnulacionForm)
from .models import Estudiante,Acudiente,EstudianteAcudiente,Grado,Grupo,PeriodoAcademico,ConceptoCobro,Matricula,Obligacion,Pago,Auditoria
from .services import crear_matricula, registrar_pago, anular_pago, auditar

def rol(*roles):
    def decorator(fn):
        @login_required
        def wrapper(request,*args,**kwargs):
            if not(request.user.is_superuser or request.user.groups.filter(name__in=roles).exists()): raise PermissionDenied('No autorizado')
            return fn(request,*args,**kwargs)
        return wrapper
    return decorator

@login_required
def inicio(request):
    return render(request,'inicio.html',{'estudiantes':Estudiante.objects.count(),'matriculas':Matricula.objects.count(),'obligaciones':Obligacion.objects.count(),'pagos':Pago.objects.filter(estado='Confirmado').aggregate(t=Sum('total'))['t'] or 0})

def editar(request,form_cls,titulo,retorno,instance=None,modulo='Académico'):
    form=form_cls(request.POST or None,instance=instance)
    if request.method=='POST' and form.is_valid():
        obj=form.save()
        auditar(request.user,modulo,'EDITAR' if instance else 'CREAR',obj,f'{titulo} - {obj}')
        messages.success(request,'Datos guardados correctamente.')
        return redirect(retorno)
    return render(request,'form.html',{'form':form,'titulo':titulo})

@rol('Secretaría académica','Administrador')
def estudiantes(request):
    q=request.GET.get('q','').strip()
    qs=Estudiante.objects.all()
    if q:
        from django.db.models import Q
        qs=qs.filter(Q(documento__icontains=q)|Q(nombres__icontains=q)|Q(apellidos__icontains=q))
    return render(request,'lista.html',{'titulo':'Estudiantes','objetos':qs,'campos':['documento','nombres','apellidos','estado'],'nuevo':'estudiante_nuevo'})

@rol('Secretaría académica','Administrador')
def estudiante_nuevo(request): return editar(request,EstudianteForm,'Registrar estudiante','estudiantes',modulo='Estudiantes')
@rol('Secretaría académica','Administrador')
def estudiante_editar(request,pk): return editar(request,EstudianteForm,'Editar estudiante','estudiantes',get_object_or_404(Estudiante,pk=pk),modulo='Estudiantes')
@rol('Secretaría académica','Administrador')
def acudientes(request): return render(request,'lista.html',{'titulo':'Acudientes','objetos':Acudiente.objects.all(),'campos':['documento','nombres','apellidos','telefono'],'nuevo':'acudiente_nuevo'})
@rol('Secretaría académica','Administrador')
def acudiente_nuevo(request): return editar(request,AcudienteForm,'Registrar acudiente','acudientes',modulo='Acudientes')
@rol('Secretaría académica','Administrador')
def asociar(request): return editar(request,EstudianteAcudienteForm,'Asociar estudiante y acudiente','acudientes',modulo='Acudientes')
@rol('Secretaría académica','Administrador')
def grupos(request): return render(request,'lista.html',{'titulo':'Grupos','objetos':Grupo.objects.all(),'campos':['grado','nombre','jornada','activo'],'nuevo':'grupo_nuevo'})
@rol('Secretaría académica','Administrador')
def grupo_nuevo(request): return editar(request,GrupoForm,'Nuevo grupo','grupos',modulo='Oferta académica')
@rol('Secretaría académica','Administrador')
def periodo_nuevo(request): return editar(request,PeriodoForm,'Nuevo período','inicio',modulo='Oferta académica')
@rol('Tesorería','Administrador')
def concepto_nuevo(request): return editar(request,ConceptoForm,'Nuevo concepto de cobro','inicio',modulo='Finanzas')
@rol('Secretaría académica','Administrador')
def matriculas(request): return render(request,'lista.html',{'titulo':'Matrículas','objetos':Matricula.objects.select_related('estudiante','grupo','periodo'),'campos':['numero','estudiante','grupo','periodo','estado'],'nuevo':'matricula_nueva'})
@rol('Secretaría académica','Administrador')
def matricula_nueva(request):
    f=MatriculaForm(request.POST or None)
    if request.method=='POST' and f.is_valid():
        try:
            m=crear_matricula(f,request.user)
            messages.success(request,f'Matrícula {m.numero} creada y obligaciones generadas.')
            return redirect('matriculas')
        except ValidationError as e: f.add_error(None,e)
    return render(request,'form.html',{'form':f,'titulo':'Registrar matrícula'})
@rol('Tesorería','Administrador')
def obligaciones(request): return render(request,'obligaciones.html',{'objetos':Obligacion.objects.select_related('matricula__estudiante','concepto').all()})
@rol('Tesorería','Administrador')
def pago_nuevo(request):
    f=PagoForm(request.POST or None)
    if request.method=='POST' and f.is_valid():
        try:
            p=registrar_pago(f.cleaned_data['obligacion'].id,f.cleaned_data['valor'],f.cleaned_data['referencia'],request.user)
            messages.success(request,f'Pago {p.referencia} confirmado y saldo actualizado.')
            return redirect('obligaciones')
        except ValidationError as e: f.add_error(None,e)
    return render(request,'form.html',{'form':f,'titulo':'Registrar pago o abono'})
@rol('Tesorería','Administrador')
def pagos(request): return render(request,'lista.html',{'titulo':'Pagos','objetos':Pago.objects.all().order_by('-fecha'),'campos':['referencia','fecha','total','estado'],'nuevo':'pago_nuevo'})
@rol('Administrador')
def pago_anular(request,pk):
    p=get_object_or_404(Pago,pk=pk)
    f=AnulacionForm(request.POST or None)
    if request.method=='POST' and f.is_valid():
        try:
            anular_pago(p.pk,f.cleaned_data['justificacion'],request.user)
            messages.success(request,'Pago anulado y registrado en auditoría.')
            return redirect('pagos')
        except ValidationError as e: f.add_error(None,e)
    return render(request,'form.html',{'form':f,'titulo':f'Anular pago {p.referencia}'})
@rol('Director','Tesorería','Administrador')
def cartera(request):
    obs=list(Obligacion.objects.select_related('matricula__estudiante','concepto'))
    pendientes=[o for o in obs if not o.anulada and o.saldo>0]
    return render(request,'cartera.html',{'pendientes':pendientes,'saldo_total':sum((o.saldo for o in pendientes),Decimal('0.00'))})
@rol('Director','Tesorería','Administrador','Secretaría académica')
def reporte(request):
    """Diez reportes reales con filtros y exportación a Excel/PDF."""
    from .reportes import obtener_reporte, generar_excel, generar_pdf, DEFINICIONES
    codigo=request.GET.get('tipo','matriculados')
    if codigo not in DEFINICIONES: codigo='matriculados'
    periodo=request.GET.get('periodo','').strip()
    estudiante=request.GET.get('estudiante','').strip()
    estado=request.GET.get('estado','').strip()
    grado=request.GET.get('grado','').strip()
    columnas,filas=obtener_reporte(codigo,periodo=periodo,estudiante=estudiante,estado=estado,grado=grado)
    formato=request.GET.get('descargar','')
    if formato=='xlsx': return generar_excel(codigo,columnas,filas)
    if formato=='pdf': return generar_pdf(codigo,columnas,filas)
    return render(request,'reportes_final.html',{
        'tipos':DEFINICIONES,'codigo':codigo,'titulo_reporte':DEFINICIONES[codigo],
        'columnas':columnas,'filas':filas,'periodo':periodo,'estudiante':estudiante,'estado':estado,'grado':grado})

@rol('Administrador')
def auditoria(request): return render(request,'lista.html',{'titulo':'Auditoría','objetos':Auditoria.objects.select_related('usuario')[:100],'campos':['fecha','usuario','modulo','accion','descripcion']})

@login_required
def estado_cuenta(request):
    """Consulta de estado individual, limitada al estudiante identificado en sesión."""
    # Para los roles institucionales se usa el reporte filtrado. No exponer otros estudiantes.
    from django.core.exceptions import PermissionDenied
    if request.user.is_superuser or request.user.groups.filter(name__in=['Administrador','Tesorería','Director']).exists():
        return redirect('cartera')
    raise PermissionDenied('Su cuenta aún no está asociada a un estudiante. Solicite vinculación a administración.')
