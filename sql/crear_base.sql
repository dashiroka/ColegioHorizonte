-- Ejecutar como usuario administrador de PostgreSQL en pgAdmin Query Tool.
-- Sustituir la contraseña antes de ejecutar; no publicar credenciales reales.
CREATE ROLE colegio_app LOGIN PASSWORD 'CAMBIAR_ESTA_CLAVE';
CREATE DATABASE colegio_horizonte OWNER colegio_app ENCODING 'UTF8';
-- Nota: CREATE DATABASE debe ejecutarse fuera de un bloque de transacción.
-- Las tablas se crean mediante: python manage.py migrate --run-syncdb
