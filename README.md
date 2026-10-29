# Sistema Integral de Gestión — Delegaciones Municipales de La Serena

Evaluación Sumativa N°3 · Django 6 · Bootstrap 5 · MySQL · AWS EC2

Aplicación web de seguimiento de solicitudes (tickets) vecinales. **No usa Django Admin**: toda la
gestión se hace con vistas, formularios y templates propios, con autenticación, perfiles con permisos,
dashboards por rol y recuperación de contraseña por correo.

## Funcionalidades

| Requerimiento | Implementación |
|---|---|
| Login / logout / vistas protegidas | `LoginView`, `LogoutView` (POST), `PermissionRequiredMixin` |
| 3 perfiles | Grupos **Administrador**, **Supervisor**, **Administrativo** con permisos distintos (`usuariosApp/perfiles.py`) |
| Dashboards por perfil | `/dashboard/` muestra una plantilla distinta según el perfil |
| Recuperación de contraseña | Token seguro de Django + correo con enlace (expira en 1 hora) |
| Mantenedores CRUD (con búsqueda) | Solicitudes, Delegaciones, Categorías, Funcionarios y Usuarios del sistema |
| Transacción | **Registrar atención**: crea `AtencionSolicitud` y actualiza `Solicitud` en una transacción atómica |
| Gestión de usuarios | Crear usuarios, asignar perfil (grupo), activar/desactivar, vincular con funcionario |

### Permisos por perfil

| Módulo | Administrador | Supervisor | Administrativo |
|---|---|---|---|
| Solicitudes | ver, crear, editar, eliminar | ver, crear, editar | ver, crear |
| Delegaciones / Categorías | CRUD completo | ver, crear, editar | solo ver |
| Funcionarios | CRUD completo | solo ver | sin acceso |
| Registrar atención (transacción) | sí | sí | sí |
| Usuarios del sistema | CRUD completo | sin acceso | sin acceso |

Un usuario con `is_superuser` se trata como Administrador.

## Instalación local

```bash
python -m venv venv && source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                  # editar SECRET_KEY, BD y correo
python manage.py migrate
python manage.py cargar_datos                         # roles + datos de ejemplo + 3 cuentas demo
python manage.py runserver
```

Para probar sin MySQL: `DB_ENGINE=sqlite` en `.env`.

Cuentas demo creadas por `cargar_datos` (contraseña `Muni2026!`, cambiable con `--password`):

| Usuario | Perfil |
|---|---|
| `admin` | Administrador |
| `supervisor` | Supervisor |
| `administrativo` | Administrativo |

Use `--admin-email tucorreo@dominio.cl` (y equivalentes) para que los correos de las cuentas demo
sean direcciones reales y se pueda demostrar la recuperación de contraseña.

## Recuperación de contraseña (correo)

- **Desarrollo**: `EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend` → el correo se imprime en la terminal.
- **Producción / revisión**: SMTP real, por ejemplo Gmail con *contraseña de aplicación*:

```
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu_cuenta@gmail.com
EMAIL_HOST_PASSWORD=xxxx xxxx xxxx xxxx
DEFAULT_FROM_EMAIL=Municipalidad La Serena <tu_cuenta@gmail.com>
```

Flujo: `/recuperar/` → correo con enlace `/recuperar/<uid>/<token>/` → nueva contraseña → confirmación → login.

## Despliegue en AWS EC2 (Ubuntu)

```bash
sudo apt update && sudo apt install -y python3-venv python3-dev default-libmysqlclient-dev build-essential pkg-config nginx mysql-server
git clone <URL_DEL_REPOSITORIO> && cd Eva1
python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt
cp .env.example .env && nano .env     # DEBUG=False, ALLOWED_HOSTS=<IP_PUBLICA>, CSRF_TRUSTED_ORIGINS=http://<IP_PUBLICA>
python manage.py migrate && python manage.py cargar_datos && python manage.py collectstatic --noinput
gunicorn config.wsgi:application --bind 0.0.0.0:8000     # o detrás de nginx
```

Abrir el puerto en el *Security Group* de la instancia (80/8000). Con `DEBUG=False` los estáticos deben
servirse con nginx apuntando a `staticfiles/`.

## Estructura

```
config/            settings (variables de entorno), urls
usuariosApp/       perfiles, login, dashboards, funcionarios, gestión de usuarios, mixins CRUD
solicitudesApp/    solicitudes, delegaciones, categorías, transacción de atención
templates/         base, registration/ (login y recuperación), crud/ (genéricos), dashboards
data/              JSON de ejemplo usados por `cargar_datos`
docs/              documento técnico
```

## Migraciones

`0001` (evaluaciones anteriores) + `0002` en cada app: catálogos `Delegacion` y `Categoria`, relaciones
con `Solicitud`, `AtencionSolicitud` y vínculo `Usuario.user`. Si la base de datos tenía datos de la
evaluación anterior, ejecute `python manage.py cargar_datos` tras migrar.
