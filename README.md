# Colegio Horizonte — Entrega final v1.0.0 (propuesta de actualización)

**Institución ficticia:** Colegio Horizonte, colegio privado de grados 6º a 11º en Colombia.

**Finalidad:** registro de estudiantes y acudientes, grados, períodos, matrícula, generación de obligaciones, pagos, abonos, cartera y auditoría.

**Tecnologías:** Django 5.2 / Python 3.12+ / PostgreSQL 18 / HTML / CSS / JavaScript / ReportLab / OpenPyXL.

> Importante: este repositorio contiene una **aplicación web de gestión**, no una página informativa. El enunciado del taller admite soluciones **web o de escritorio**. Si el docente requiere explícitamente escritorio, deberá realizarse una interfaz de escritorio alternativa.

## Equipo

Añadir los nombres de todos los integrantes antes de la entrega.

## Instalación rápida en Windows

1. Instalar Python 3.12+ y PostgreSQL 18. Crear una base de datos vacía `colegio_horizonte` y un usuario de conexión con privilegios sobre ella.
2. Descargar el proyecto desde GitHub con `git clone` o mediante **Code > Download ZIP**.
3. Dentro de la carpeta que contiene `manage.py`:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

4. Editar `.env` para establecer `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `SECRET_KEY` (genera una con `python -c "import secrets; print(secrets.token_urlsafe(50))"`). No subir `.env`.
5. En un **PostgreSQL vacío**, ejecutar:

```powershell
python manage.py makemigrations academico
python manage.py migrate
python manage.py preparar_demo
python manage.py createsuperuser
python manage.py cargar_datos_finales
python manage.py comprobar_cantidades
python manage.py runserver
```

6. Abrir `http://127.0.0.1:8000/`. Para administración usar `/admin/`.
7. La carga imprime **una sola vez** las contraseñas temporales de los cinco usuarios ficticios. Guárdalas localmente y no las publiques.

**Nota para usuarios de la entrega 2:** Si ya existe una base de datos con migraciones aplicadas, **NO** eliminarla ni reconstruirla. Haz una copia de respaldo y usa `python manage.py migrate` para conservar los datos. La carga `cargar_datos_finales` agrega estudiantes ficticios marcados con prefijo `FICT-` para no confundirlos con los anteriores.

## Roles y seguridad

Perfiles de prueba: Administrador, Director, Secretaría académica, Tesorería y Docente. El backend rechaza con HTTP 403 las operaciones no permitidas. Django utiliza hashing seguro, protección CSRF y consultas ORM parametrizadas. En producción, utilizar HTTPS y configurar `DEBUG=False`.

## Módulos

- Estudiantes, acudientes y asociación con responsable de pago.
- Grados, grupos, períodos y conceptos de cobro.
- Matrículas con identificadores únicos y restricciones de duplicidad.
- Obligaciones, pagos parciales y completos, anulación auditada.
- Cartera y diez reportes exportables a PDF y Excel (filtrados por estudiante, período, grado y estado donde corresponda).
- Auditoría de altas y anulaciones.

## Verificación

```powershell
python manage.py check
python manage.py test academico
```

Los resultados reales deben registrarse en `docs/Pruebas_Finales.md` tras ejecutar los comandos. Adjuntar capturas reales en `screenshots/`. Nunca presentar pruebas no ejecutadas como satisfactorias.

## Manuales y fuentes

- `docs/Manual_Instalacion_Final.pdf`
- `docs/Manual_Usuario_Final.pdf`
- `docs/Informe_Final.pdf`
- `docs/Diccionario_Final.pdf`
- `docs/Pruebas_Finales.md`
- `docs/Guion_Sustentacion.md`

## Historial y versión

Entrega 1: análisis y diseño. Entrega 2: Django, PostgreSQL, matrícula y pagos. Entrega 3: reportes ampliados, datos ficticios y documentación. Crear etiqueta `v1.0.0` **solo después de comprobar en el equipo**.

## Uso de IA (declaración)

Se utilizó ChatGPT (modelo GPT-6) como apoyo en el análisis del enunciado, redacción de documentación y propuesta de código. Los integrantes deben revisar, comprender, ejecutar, probar y explicar cada módulo; reemplazar esta declaración si corresponde a la experiencia real del equipo.

### Ejemplos de instrucciones utilizadas

- «Preparar las tres entregas para un colegio de bachillerato ficticio».
- «Generar pruebas funcionales de matrícula y abonos parciales».
- «Añadir reportes financieros con datos reales de PostgreSQL».

## Autoría y confidencialidad

Solo datos ficticios. `.env`, credenciales, usuarios reales y archivos temporales están excluidos del repositorio.
