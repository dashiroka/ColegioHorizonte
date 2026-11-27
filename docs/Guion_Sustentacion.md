# Guion de sustentación (28 de noviembre de 2026)

## Presentación técnica (2 minutos)

El Colegio Horizonte administraba matrículas y pensiones manualmente. Construimos una aplicación de gestión para registrar estudiantes, acudientes y grados; matricular por período; generar obligaciones; recibir pagos completos y parciales y consultar cartera.

Arquitectura de tres capas: HTML/CSS y navegador, Python/Django para reglas y permisos y PostgreSQL para persistencia. El control de acceso se realiza en el servidor por roles. Los pagos se procesan con transacciones y auditan. Django permite instalar la aplicación en un equipo distinto con las dependencias del README.

## Demostración (5 minutos)

1. Entrar con administrador; mostrar perfiles.
2. Buscar un estudiante de prueba por documento.
3. Crear uno, asociar acudiente y asignar grupo.
4. Registrar matrícula del período 2027; comprobar que se crean obligaciones.
5. Registrar un pago completo en una obligación.
6. Registrar un abono parcial de otra obligación.
7. Mostrar saldo, cartera y estado de cuenta con filtros.
8. Abrir reporte de matrícula y exportar PDF; abrir reporte de ingresos y exportar Excel.
9. Revisar auditoría.
10. Entrar como Secretaría e intentar pagar (403); repetir como Tesorería (permitido).
11. Enseñar repositorio, etiqueta v1.0.0 e instrucciones de instalación.

**Nota:** la interfaz existente es una aplicación web de gestión; el taller acepta aplicación web o escritorio, pero confirmar con el profesor su interpretación.
