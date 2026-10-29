"""
Carga datos iniciales: roles (grupos/permisos), catálogos, funcionarios y solicitudes
desde data/*.json, y crea tres cuentas de demostración (una por perfil).

Uso:
    python manage.py cargar_datos
    python manage.py cargar_datos --password 'Muni2026!' --admin-email correo@dominio.cl
"""
import json
from datetime import date

from django.contrib.auth.models import Group, User
from django.core.management.base import BaseCommand
from django.conf import settings

from solicitudesApp.models import Categoria, Delegacion, Solicitud
from usuariosApp.models import Usuario
from usuariosApp.perfiles import ADMINISTRADOR, ADMINISTRATIVO, SUPERVISOR, sincronizar_roles
from usuariosApp.validators import calcular_dv

NO_TERRITORIALES = {'Coordinación General', 'Todas las delegaciones'}


def _leer(nombre):
    ruta = settings.BASE_DIR / 'data' / nombre
    with open(ruta, encoding='utf-8') as f:
        return json.load(f)


def _rut_valido(rut):
    """Re-calcula el dígito verificador para que los RUT de ejemplo pasen la validación."""
    cuerpo = ''.join(c for c in rut.split('-')[0] if c.isdigit())
    return f"{int(cuerpo):,}".replace(',', '.') + '-' + calcular_dv(cuerpo)


class Command(BaseCommand):
    help = 'Crea roles, datos de ejemplo y cuentas de demostración.'

    def add_arguments(self, parser):
        parser.add_argument('--password', default='Muni2026!', help='Contraseña de las cuentas demo.')
        parser.add_argument('--admin-email', default='admin@laserena.cl')
        parser.add_argument('--supervisor-email', default='supervisor@laserena.cl')
        parser.add_argument('--administrativo-email', default='administrativo@laserena.cl')
        parser.add_argument('--reset-passwords', action='store_true',
                            help='Restablece la contraseña si las cuentas demo ya existen.')

    def handle(self, *args, **o):
        resumen = sincronizar_roles()
        self.stdout.write(self.style.SUCCESS(f'Roles sincronizados: {resumen}'))

        usuarios_json = _leer('usuarios.json')
        solicitudes_json = _leer('solicitudes.json')

        # Catálogos
        nombres_deleg = {s['delegacion_territorial'] for s in solicitudes_json}
        nombres_deleg |= {u['delegacion_asignada'] for u in usuarios_json} - NO_TERRITORIALES
        for n in sorted(nombres_deleg):
            Delegacion.objects.get_or_create(nombre=n, defaults={'descripcion': f'Delegación {n}'})
        for n in sorted({s['tipo_categoria'] for s in solicitudes_json}):
            Categoria.objects.get_or_create(nombre=n, defaults={'descripcion': f'Solicitudes de {n.lower()}'})

        # Funcionarios
        for u in usuarios_json:
            Usuario.objects.update_or_create(
                id_usuario=u['id_usuario'],
                defaults={
                    'nombre_completo': u['nombre_completo'], 'rut': _rut_valido(u['rut']),
                    'rol': u['rol'], 'delegacion_asignada': u['delegacion_asignada'],
                    'correo_muni': u['correo_muni'].lower(), 'estado_cuenta': u['estado_cuenta'],
                    'foto_perfil': u['foto_perfil'],
                })

        # Solicitudes
        for s in solicitudes_json:
            estado = s['estado_tramite'] if s['estado_tramite'] in ('Pendiente', 'En proceso', 'Realizado', 'Cancelado') else 'Pendiente'
            Solicitud.objects.update_or_create(
                id_solicitud=s['id_solicitud'],
                defaults={
                    'fecha_registro': date.fromisoformat(s['fecha_registro']),
                    'fecha_comprometida': date.fromisoformat(s['fecha_comprometida']),
                    'delegacion': Delegacion.objects.get(nombre=s['delegacion_territorial']),
                    'categoria': Categoria.objects.get(nombre=s['tipo_categoria']),
                    'descripcion_requerimiento': s['descripcion_requerimiento'],
                    'area_responsable': s['area_responsable'],
                    'funcionario_responsable': Usuario.objects.filter(nombre_completo=s['funcionario_responsable']).first(),
                    'solicitante_muni': s['solicitante_muni'],
                    'estado_tramite': estado,
                    'nivel_prioridad': s['nivel_prioridad'],
                    'avance_porcentaje': s['avance_porcentaje'],
                    'imagen_evidencia': s['imagen_evidencia'],
                })

        # Cuentas demo (una por perfil)
        demos = [
            ('admin', ADMINISTRADOR, o['admin_email'], 'Ana', 'Torres', 'USR-002'),
            ('supervisor', SUPERVISOR, o['supervisor_email'], 'Pedro', 'Soto', 'USR-004'),
            ('administrativo', ADMINISTRATIVO, o['administrativo_email'], 'Carlos', 'Mendoza', 'USR-001'),
        ]
        for username, perfil, email, nombre, apellido, id_func in demos:
            user, creado = User.objects.get_or_create(
                username=username,
                defaults={'email': email, 'first_name': nombre, 'last_name': apellido})
            if creado or o['reset_passwords']:
                user.set_password(o['password'])
            user.email = email
            user.save()
            user.groups.set([Group.objects.get(name=perfil)])
            func = Usuario.objects.filter(id_usuario=id_func, user__isnull=True).first()
            if func:
                func.user = user
                func.save(update_fields=['user'])
            self.stdout.write(f'  {perfil:15s} usuario={username:15s} correo={email}'
                              + (f' contraseña={o["password"]}' if creado or o['reset_passwords'] else ' (ya existía)'))
        self.stdout.write(self.style.SUCCESS('Datos cargados correctamente.'))
