from decimal import Decimal
from datetime import date
from django.contrib.auth.models import Group, User
from django.core.management.base import BaseCommand
from academico.models import Grado,Grupo,PeriodoAcademico,ConceptoCobro
class Command(BaseCommand):
    help='Crea roles y catálogos; usuarios se crean de forma segura por consola.'
    def handle(self,*args,**kwargs):
        for r in ['Administrador','Secretaría académica','Tesorería','Director']:
            Group.objects.get_or_create(name=r)
        for nombre in ['Sexto','Séptimo','Octavo','Noveno','Décimo','Undécimo']:
            g,_=Grado.objects.get_or_create(nombre=nombre)
            Grupo.objects.get_or_create(grado=g,nombre='A',jornada='Mañana')
        PeriodoAcademico.objects.get_or_create(nombre='2026',defaults={'fecha_inicio':date(2026,2,1),'fecha_fin':date(2026,11,30)})
        ConceptoCobro.objects.get_or_create(nombre='Matrícula 2026',defaults={'tipo':'MATRICULA','valor_base':Decimal('350000')})
        ConceptoCobro.objects.get_or_create(nombre='Pensión 2026',defaults={'tipo':'PENSION','valor_base':Decimal('250000')})
        self.stdout.write(self.style.SUCCESS('Catálogos cargados. Cree usuarios con createsuperuser y admin /admin/.'))
