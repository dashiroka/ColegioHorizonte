from datetime import date
from decimal import Decimal
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase
from .models import Estudiante,Grado,Grupo,PeriodoAcademico,ConceptoCobro,Matricula,Obligacion,Pago
from .forms import MatriculaForm
from .services import crear_matricula,registrar_pago,anular_pago
class CicloTest(TestCase):
    def setUp(self):
        self.user=User.objects.create_user('cajero',password='PruebaSegura1234!')
        self.est=Estudiante.objects.create(tipo_documento='TI',documento='TEST-01',nombres='Laura',apellidos='Ejemplo',fecha_nacimiento=date(2011,1,2),direccion='Ficticia',telefono='000')
        grado=Grado.objects.create(nombre='Sexto'); self.grupo=Grupo.objects.create(grado=grado,nombre='A',jornada='Mañana')
        self.periodo=PeriodoAcademico.objects.create(nombre='2026',fecha_inicio=date(2026,2,1),fecha_fin=date(2026,11,30))
        self.matr=ConceptoCobro.objects.create(nombre='Matrícula',tipo='MATRICULA',valor_base=Decimal('350000'))
        ConceptoCobro.objects.create(nombre='Pensión',tipo='PENSION',valor_base=Decimal('250000'))
    def test_flujo_pago_parcial_y_anulacion(self):
        form=MatriculaForm(data={'estudiante':self.est.pk,'grupo':self.grupo.pk,'periodo':self.periodo.pk,'fecha':'2026-02-01','valor_matricula':'350000.00','descuento':'0'})
        self.assertTrue(form.is_valid(),form.errors)
        m=crear_matricula(form,self.user)
        o=Obligacion.objects.get(matricula=m,concepto=self.matr)
        self.assertEqual(o.saldo,Decimal('350000'))
        p=registrar_pago(o.pk,Decimal('100000'),'ABONO-001',self.user)
        self.assertEqual(o.saldo,Decimal('250000'))
        with self.assertRaises(ValidationError): registrar_pago(o.pk,Decimal('300000'),'ABONO-002',self.user)
        anular_pago(p.pk,'Error de registro',self.user)
        self.assertEqual(o.saldo,Decimal('350000'))
    def test_documento_duplicado(self):
        with self.assertRaises(Exception):
            Estudiante.objects.create(tipo_documento='TI',documento='TEST-01',nombres='Otro',apellidos='Ejemplo',fecha_nacimiento=date(2010,1,1),direccion='Ficticia',telefono='000')

from django.test import Client
from django.contrib.auth.models import Group

class PermisosTest(TestCase):
    def setUp(self):
        self.secretaria=User.objects.create_user('secretaria_prueba',password='PruebaSegura1234!')
        self.tesoreria=User.objects.create_user('tesoreria_prueba',password='PruebaSegura1234!')
        s,_=Group.objects.get_or_create(name='Secretaría académica'); t,_=Group.objects.get_or_create(name='Tesorería')
        self.secretaria.groups.add(s);self.tesoreria.groups.add(t)
    def test_secretaria_no_puede_registrar_pago(self):
        self.client.force_login(self.secretaria)
        self.assertEqual(self.client.get('/pagos/nuevo/').status_code,403)
    def test_tesoreria_si_puede_abrir_formulario(self):
        self.client.force_login(self.tesoreria)
        self.assertEqual(self.client.get('/pagos/nuevo/').status_code,200)
    def test_estudiante_sin_permisos_no_ve_cartera(self):
        u=User.objects.create_user('estudiante_prueba',password='PruebaSegura1234!')
        self.client.force_login(u)
        self.assertEqual(self.client.get('/cartera/').status_code,403)
    def test_usuario_anonimo_redirigido_al_login(self):
        self.assertEqual(self.client.get('/pagos/nuevo/').status_code,302)

class BloqueoLoginTest(TestCase):
    def test_cinco_intentos_invalidos_bloquean(self):
        User.objects.create_user('usuario_bloqueo',password='ClaveCorrectaMuySegura123!')
        for _ in range(5):
            self.client.post('/login/',{'username':'usuario_bloqueo','password':'Incorrecta1!'})
        self.assertEqual(self.client.post('/login/',{'username':'usuario_bloqueo','password':'Incorrecta1!'}).status_code,429)
