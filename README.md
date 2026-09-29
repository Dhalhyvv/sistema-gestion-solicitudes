# Sistema de Gestión de Solicitudes

Aplicación web Django para el seguimiento de solicitudes territoriales de la Municipalidad de La Serena. Evaluación Sumativa N°2, Primavera 2026.

## Tecnologías

Python, Django, MariaDB (phpMyAdmin), Bootstrap, AWS EC2 (Amazon Linux 2023), Git y GitHub.

## Aplicaciones

- usuariosApp: modelo Usuario (funcionarios municipales).
- solicitudesApp: modelo Solicitud, con ForeignKey a Usuario.

## Puesta en marcha

    git clone git@github.com:Dhalhyvv/sistema-gestion-solicitudes.git
    cd sistema-gestion-solicitudes
    python3 -m venv venv
    source venv/bin/activate
    pip install django mysqlclient python-dotenv
    python manage.py migrate
    python manage.py createsuperuser
    python manage.py runserver 0.0.0.0:8000

Se requiere un archivo `.env` con DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT y ALLOWED_HOSTS.

## Autor

Javier Ibarra, INACAP.
