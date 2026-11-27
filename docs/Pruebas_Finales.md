# Pruebas funcionales y de seguridad — completar con evidencia real

**Estado:** pruebas propuestas y automatizadas, aún no verificadas en el equipo de entrega 3.

| Caso | Entrada / procedimiento | Resultado esperado | Resultado obtenido | Captura |
|---|---|---|---|---|
| PF01 | Crear estudiante ficticio | Aparece en listado y BD | Pendiente | |
| PF02 | Documento duplicado | Rechazo por unicidad | Pendiente | |
| PF03 | Crear matrícula | ID único, obligaciones automáticas | Pendiente | |
| PF04 | Abonar 100.000 a matrícula de 350.000 | Saldo 250.000 | Pendiente | |
| PF05 | Intentar abonar 300.000 al saldo 250.000 | Rechazo del pago | Pendiente | |
| PF06 | Abonar total remanente | Saldo 0, Pagado | Pendiente | |
| PF07 | Consultar mora y cartera | Valores consistentes | Pendiente | |
| PF08 | Anular pago como admin | Reversión y auditoría | Pendiente | |
| PF09 | 10 reportes | Datos de BD y filtros | Pendiente | |
| PF10 | Exportar un reporte PDF y otro Excel | Archivos legibles | Pendiente | |
| PS01 | Secretaría abre `/pagos/nuevo/` | HTTP 403 | Pendiente | |
| PS02 | Tesorería abre `/pagos/nuevo/` | HTTP 200 | Pendiente | |
| PS03 | Estudiante abre `/cartera/` | HTTP 403 | Pendiente | |
| PS04 | Anónimo abre URL privada | Redirigido al inicio de sesión | Pendiente | |
| PS05 | Formulario con datos inválidos | Error de validación | Pendiente | |
| PS06 | Intentos de autenticación repetidos | HTTP 429 tras 5 intentos, bloqueo temporal de 15 minutos | Pendiente de ejecución | |
| PS07 | Acceso a estado financiero ajeno | Acceso denegado | Pendiente | |
| PI01 | Instalación desde repositorio en otro PC/VM | Arranca y consulta base de datos | Pendiente | |

## Comandos para ejecutar pruebas automatizadas

`python manage.py test academico`

**No marque como aprobadas pruebas que no se hayan ejecutado.**
