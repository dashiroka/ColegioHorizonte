# Plan de pruebas funcionales preliminares (propuestas, no ejecutadas)

| ID | Prueba | Entrada | Resultado esperado |
|---|---|---|---|
| PF01 | Crear estudiante | TI TEST-01 | Guarda sin duplicar |
| PF02 | Documento duplicado | TI TEST-01 nuevamente | Rechaza por restricción UNIQUE |
| PF03 | Matrícula válida | Estudiante, sexto A, 2026, $350.000 | Matrícula y obligaciones creadas |
| PF04 | Matrícula duplicada | Mismo estudiante y período | Rechazo |
| PF05 | Pago parcial | $100.000 sobre saldo $350.000 | Saldo $250.000 |
| PF06 | Pago excesivo | $300.000 sobre saldo $250.000 | Error, pago no guardado |
| PF07 | Pago total | $250.000 restantes | Saldo $0 y estado pagado |
| PF08 | Acceso restringido | Secretaría a /pagos/nuevo/ | 403 sin modificación |
| PF09 | Anulación | Admin justifica y anula pago | Reestablece saldo, conserva historial |
| PF10 | Reporte | Exportar matrículas CSV | Registros de base de datos |

Registrar fecha, usuario, resultado real y captura de cada prueba al ejecutarlas.
