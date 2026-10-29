from django.apps import AppConfig
from django.db.models.signals import post_migrate


def _sincronizar(sender, **kwargs):
    # Se ejecuta cuando termina de migrar la última app (los permisos ya existen).
    if sender.name != 'solicitudesApp':
        return
    from .perfiles import sincronizar_roles
    sincronizar_roles()


class UsuariosappConfig(AppConfig):
    name = 'usuariosApp'
    default_auto_field = 'django.db.models.BigAutoField'

    def ready(self):
        post_migrate.connect(_sincronizar, dispatch_uid='usuariosApp.sincronizar_roles')
