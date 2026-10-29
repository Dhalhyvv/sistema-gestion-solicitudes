"""
Perfiles (grupos) del sistema y sus permisos.

Administrador   -> acceso total (todos los mantenedores, transacciones y gestión de usuarios)
Supervisor      -> permisos intermedios (opera solicitudes y catálogos, sin eliminar ni gestionar usuarios)
Administrativo  -> permisos mínimos (consulta y registro; sin modificar ni eliminar)
"""
from django.contrib.auth.models import Group, Permission

ADMINISTRADOR = 'Administrador'
SUPERVISOR = 'Supervisor'
ADMINISTRATIVO = 'Administrativo'
PERFILES = (ADMINISTRADOR, SUPERVISOR, ADMINISTRATIVO)

# (app_label, modelo) -> acciones
_TODAS = ('view', 'add', 'change', 'delete')

PERMISOS_POR_PERFIL = {
    ADMINISTRADOR: {
        ('solicitudesApp', 'solicitud'): _TODAS,
        ('solicitudesApp', 'delegacion'): _TODAS,
        ('solicitudesApp', 'categoria'): _TODAS,
        ('solicitudesApp', 'atencionsolicitud'): _TODAS,
        ('usuariosApp', 'usuario'): _TODAS,
        ('auth', 'user'): _TODAS,
        ('auth', 'group'): ('view',),
    },
    SUPERVISOR: {
        ('solicitudesApp', 'solicitud'): ('view', 'add', 'change'),
        ('solicitudesApp', 'delegacion'): ('view', 'add', 'change'),
        ('solicitudesApp', 'categoria'): ('view', 'add', 'change'),
        ('solicitudesApp', 'atencionsolicitud'): ('view', 'add'),
        ('usuariosApp', 'usuario'): ('view',),
    },
    ADMINISTRATIVO: {
        ('solicitudesApp', 'solicitud'): ('view', 'add'),
        ('solicitudesApp', 'delegacion'): ('view',),
        ('solicitudesApp', 'categoria'): ('view',),
        ('solicitudesApp', 'atencionsolicitud'): ('view', 'add'),
    },
}


def obtener_perfil(user):
    """Devuelve el nombre del perfil del usuario (o None si no tiene ninguno)."""
    if not getattr(user, 'is_authenticated', False):
        return None
    if user.is_superuser:
        return ADMINISTRADOR
    nombres = set(user.groups.values_list('name', flat=True))
    for perfil in PERFILES:
        if perfil in nombres:
            return perfil
    return None


def sincronizar_roles():
    """Crea los grupos y les asigna los permisos definidos arriba (idempotente)."""
    resumen = {}
    for perfil, modelos in PERMISOS_POR_PERFIL.items():
        grupo, _ = Group.objects.get_or_create(name=perfil)
        codigos = []
        for (app, modelo), acciones in modelos.items():
            codigos += [(app, f'{accion}_{modelo}') for accion in acciones]
        permisos = []
        for app, codename in codigos:
            try:
                permisos.append(Permission.objects.get(content_type__app_label=app, codename=codename))
            except Permission.DoesNotExist:
                continue
        grupo.permissions.set(permisos)
        resumen[perfil] = len(permisos)
    return resumen
