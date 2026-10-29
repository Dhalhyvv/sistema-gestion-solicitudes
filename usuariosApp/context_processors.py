from .perfiles import obtener_perfil


def perfil(request):
    """Expone el perfil del usuario autenticado a todos los templates."""
    return {'perfil_actual': obtener_perfil(getattr(request, 'user', None))}
