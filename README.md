# Colegio Horizonte — Segunda entrega (versión 0.2)

Sistema académico-financiero de demostración para bachillerato privado en Bogotá. **Todos los datos de prueba son ficticios.**

## Funcionalidades incluidas

- Autenticación y cierre de sesión de Django; cambio de contraseña.
- Roles `Administrador`, `Secretaría académica`, `Tesorería` y `Director` aplicados en servidor.
- Administración de estudiantes, acudientes, asociaciones, grados, grupos y períodos.
- Matrículas con número único, validación de duplicidad y generación de obligaciones.
- Configuración de conceptos de matrícula y pensión; 10 mensualidades dentro del período.
- Registro de pagos parciales y totales, validación contra sobrepago, saldo calculado a partir de pagos confirmados.
- Anulación auditada de pagos (solo administrador), cartera preliminar y CSV de matrículas.
- Registro de auditoría para operaciones de aplicación importantes.

> **Alcance de la entrega 2:** los 10 reportes definitivos, exportación PDF y ampliación de perfiles de acceso quedan para la entrega 3. No usar como sistema productivo sin pruebas y endurecimiento adicional.

## Requisitos

- Python 3.11 o posterior compatible con Django 5.2.
- PostgreSQL 15+ recomendado y su servidor iniciado; `psycopg` incluido en requirements.
- Conexión a Internet **en tu computador** para instalar las dependencias Python.

## Instalación en Windows con PostgreSQL

1. Abre `sql/crear_base.sql` en pgAdmin Query Tool y ejecuta las dos instrucciones separadas como administrador. Sustituye `CAMBIAR_ESTA_CLAVE` por una contraseña propia **antes** de ejecutar. Si el rol o la base ya existen, omite los comandos correspondientes.
2. En VS Code abre esta carpeta, inicia una terminal PowerShell y ejecuta:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

3. Edita `.env`: `DB_PASSWORD` debe ser la contraseña elegida. `SECRET_KEY` debe ser aleatoria y secreta; puedes generarla con:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

4. Crea las tablas y datos iniciales:

```powershell
python manage.py migrate --run-syncdb
python manage.py preparar_demo
python manage.py createsuperuser
python manage.py runserver
```

5. Abre `http://127.0.0.1:8000/` e inicia sesión con el usuario administrador creado.
6. En `http://127.0.0.1:8000/admin/` abre **Users**, crea tres usuarios adicionales y asígnales desde **Groups** respectivamente: `Secretaría académica`, `Tesorería` y `Director`. Se recomienda no darles `is_staff`; usarán la aplicación y no el panel de administración. El usuario administrador de Django (`superuser`) realiza la administración de usuarios y catálogos.

### Alternativa de prueba sin PostgreSQL

Para una inspección local muy rápida, cambia `DB_ENGINE=sqlite` en `.env` y ejecuta los pasos 4 y 5. **Esta alternativa es solo para pruebas y no reemplaza la demostración requerida con PostgreSQL.**

## Demostración sugerida para el profesor

1. Inicia sesión como **secretaría** y usa **Estudiantes → Nuevo registro**. Registra datos ficticios.
2. Registra un acudiente y entra a **Acudientes → Asociar**.
3. Usa **Matrículas → Nuevo registro**, elige el estudiante, grupo y período `2026`, valor `350000` y descuento `0`.
4. Comprueba en **Obligaciones** que aparece el cobro de matrícula y las pensiones correspondientes.
5. Cierra sesión y entra como **tesorería**.
6. Usa **Pagos → Registrar pago o abono**, elige la obligación de matrícula y registra un abono de `100000`, referencia `ABONO-001`.
7. En **Obligaciones**, observa saldo de `250000` y estado `Pago parcial` (si no ha vencido; si venció, muestra `Vencido` manteniendo el saldo correcto).
8. Intenta registrar `300000` sobre la misma obligación: el sistema debe rechazarlo.
9. Consulta **Cartera** y, con superusuario, **Auditoría**. Prueba que secretaría no puede acceder a `/pagos/nuevo/` (403).

## Documentos y pruebas

- `docs/Informe_Entrega2.pdf`: desarrollo, decisiones técnicas y matriz de pruebas.
- `docs/Manual_Preliminar.pdf`: instrucciones para el usuario.
- `docs/Diccionario_Datos.pdf`: estructura de tablas y relaciones.
- `academico/tests.py`: dos pruebas automatizadas propuestas. Ejecutar con `python manage.py test`.
- `docs/Registro_Evidencias.md`: lista de pantallas a capturar tras ejecución real.

## GitHub

```powershell
git init
git add .
git commit -m "Entrega 2: módulos académicos, matrícula, finanzas y seguridad"
git branch -M main
git remote add origin URL_REAL_DE_TU_REPOSITORIO
git push -u origin main
```

**Nunca subas** `.env`, `db.sqlite3`, contraseñas ni datos reales. `URL_REAL_DE_TU_REPOSITORIO` es un marcador que debes sustituir después de crear el repo en GitHub.

## Limitaciones conocidas

- No incluye todavía recuperación de contraseña por correo, protección adicional contra fuerza bruta ni los reportes finales.
- Auditoría cubre operaciones del flujo de aplicación; no audita cambios directos hechos por administradores SQL ni cada edición del panel Django Admin.
- No incluye exportación PDF ni conciliación bancaria.
- El cálculo del estado `Vencido` prioriza la fecha de vencimiento sobre el estado `Pago parcial`. Los abonos continúan acumulados y no se pierde el saldo.
