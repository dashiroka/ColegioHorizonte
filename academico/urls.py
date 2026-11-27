from django.urls import path
from . import views
urlpatterns=[
 path('',views.inicio,name='inicio'),
 path('estudiantes/',views.estudiantes,name='estudiantes'),
 path('estudiantes/nuevo/',views.estudiante_nuevo,name='estudiante_nuevo'),
 path('estudiantes/<int:pk>/editar/',views.estudiante_editar,name='estudiante_editar'),
 path('acudientes/',views.acudientes,name='acudientes'),
 path('acudientes/nuevo/',views.acudiente_nuevo,name='acudiente_nuevo'),
 path('acudientes/asociar/',views.asociar,name='asociar'),
 path('grupos/',views.grupos,name='grupos'),path('grupos/nuevo/',views.grupo_nuevo,name='grupo_nuevo'),
 path('periodos/nuevo/',views.periodo_nuevo,name='periodo_nuevo'),
 path('conceptos/nuevo/',views.concepto_nuevo,name='concepto_nuevo'),
 path('matriculas/',views.matriculas,name='matriculas'),path('matriculas/nueva/',views.matricula_nueva,name='matricula_nueva'),
 path('obligaciones/',views.obligaciones,name='obligaciones'),
 path('pagos/',views.pagos,name='pagos'),path('pagos/nuevo/',views.pago_nuevo,name='pago_nuevo'),
 path('pagos/<int:pk>/anular/',views.pago_anular,name='pago_anular'),
 path('estado-cuenta/',views.estado_cuenta,name='estado_cuenta'),
 path('cartera/',views.cartera,name='cartera'),path('reportes/',views.reporte,name='reportes'),path('auditoria/',views.auditoria,name='auditoria'),
]
