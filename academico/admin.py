from django.contrib import admin
from .models import Estudiante,Acudiente,EstudianteAcudiente,Grado,Grupo,PeriodoAcademico,ConceptoCobro,Matricula,Obligacion,Pago,DetallePago,Auditoria
for model in [Estudiante,Acudiente,EstudianteAcudiente,Grado,Grupo,PeriodoAcademico,ConceptoCobro,Matricula,Obligacion,Pago,DetallePago,Auditoria]:
    admin.site.register(model)
