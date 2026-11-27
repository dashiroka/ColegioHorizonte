from django.core.management.base import BaseCommand
from django.contrib.auth.models import User,Group
from academico.models import Estudiante,Acudiente,Grado,Grupo,PeriodoAcademico,Matricula,Obligacion,Pago
class Command(BaseCommand):
    help='Muestra las cantidades reales cargadas para la sustentación.'
    def handle(self,*args,**options):
        data=[('Usuarios',User.objects.count(),5),('Roles',Group.objects.count(),5),('Estudiantes',Estudiante.objects.count(),30),('Acudientes',Acudiente.objects.count(),15),('Grados',Grado.objects.count(),3),('Grupos',Grupo.objects.count(),3),('Períodos',PeriodoAcademico.objects.count(),1),('Matrículas',Matricula.objects.count(),30),('Obligaciones',Obligacion.objects.count(),60),('Pagos',Pago.objects.count(),20)]
        for name,count,minimo in data:
            self.stdout.write(f'{name}: {count} / mínimo {minimo} - {"OK" if count>=minimo else "PENDIENTE"}')
