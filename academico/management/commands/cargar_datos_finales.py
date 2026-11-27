"""Datos ficticios reproducibles para sustentación. No sobrescribe registros existentes."""
from datetime import date
from decimal import Decimal
import secrets
from django.contrib.auth.models import Group,User
from django.core.management.base import BaseCommand
from django.db import transaction
from academico.models import Estudiante,Acudiente,EstudianteAcudiente,Grado,Grupo,PeriodoAcademico,ConceptoCobro,Matricula,Pago,Obligacion
from academico.forms import MatriculaForm
from academico.services import crear_matricula,registrar_pago

class Command(BaseCommand):
    help='Carga 30 estudiantes, 15 acudientes, 30 matrículas, 60+ obligaciones, 20 pagos y 5 usuarios ficticios.'
    @transaction.atomic
    def handle(self,*args,**kwargs):
        roles=['Administrador','Director','Secretaría académica','Tesorería','Docente']
        for nombre in roles: Group.objects.get_or_create(name=nombre)
        users=[('demo_admin','Administrador'),('demo_director','Director'),('demo_secretaria','Secretaría académica'),('demo_tesoreria','Tesorería'),('demo_docente','Docente')]
        for username,rol in users:
            u,created=User.objects.get_or_create(username=username,defaults={'is_active':True})
            if created:
                password=secrets.token_urlsafe(12)
                u.set_password(password);u.save()
                self.stdout.write(f'CREDENCIAL DE PRUEBA (guardar fuera de GitHub): {username} / {password}')
            u.groups.add(Group.objects.get(name=rol))
        operador=User.objects.get(username='demo_admin')
        for grado_nombre in ['Sexto','Séptimo','Octavo','Noveno','Décimo','Undécimo']:
            g,_=Grado.objects.get_or_create(nombre=grado_nombre)
            Grupo.objects.get_or_create(grado=g,nombre='A',jornada='Mañana')
        periodo,_=PeriodoAcademico.objects.get_or_create(nombre='2027',defaults={'fecha_inicio':date(2027,2,1),'fecha_fin':date(2027,11,30)})
        ConceptoCobro.objects.get_or_create(nombre='Matrícula 2027',defaults={'tipo':'MATRICULA','valor_base':Decimal('350000')})
        ConceptoCobro.objects.get_or_create(nombre='Pensión 2027',defaults={'tipo':'PENSION','valor_base':Decimal('250000')})
        grupos=list(Grupo.objects.filter(nombre='A',jornada='Mañana').select_related('grado').order_by('grado__nombre'))
        for i in range(1,16):
            Acudiente.objects.get_or_create(documento=f'FICT-AC-{i:03d}',defaults={
                'nombres':f'Acudiente{i}','apellidos':'Demostracion','telefono':'3000000000','correo':f'acudiente{i}@example.com'})
        for i in range(1,31):
            e,_=Estudiante.objects.get_or_create(tipo_documento='TI',documento=f'FICT-EST-{i:03d}',defaults={
                'nombres':f'Estudiante{i}','apellidos':'Ejemplo','fecha_nacimiento':date(2011,1,15),
                'direccion':'Dirección ficticia 100','telefono':'3000000000','correo':f'estudiante{i}@example.com'})
            a=Acudiente.objects.get(documento=f'FICT-AC-{((i-1)//2)+1:03d}')
            EstudianteAcudiente.objects.get_or_create(estudiante=e,acudiente=a,defaults={'parentesco':'Acudiente','responsable_pago':True})
            m=Matricula.objects.filter(estudiante=e,periodo=periodo).first()
            if m is None:
                data={'estudiante':e.pk,'grupo':grupos[(i-1)%len(grupos)].pk,'periodo':periodo.pk,
                      'fecha':'2027-02-01','valor_matricula':'350000','descuento':'0'}
                form=MatriculaForm(data=data)
                if not form.is_valid(): raise ValueError(str(form.errors))
                m=crear_matricula(form,operador)
            if i<=20:
                oblig=m.obligaciones.order_by('pk').first()
                if not Pago.objects.filter(referencia=f'DEMO-2027-{i:03d}').exists():
                    registrar_pago(oblig.pk,Decimal('100000') if i%2 else Decimal('350000'),f'DEMO-2027-{i:03d}',operador)
        self.stdout.write(self.style.SUCCESS('Datos ficticios listos. Verificar conteos en /admin y reportes.'))
