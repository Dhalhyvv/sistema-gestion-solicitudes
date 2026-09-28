from django.contrib import admin
from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    search_fields = [
        'id_usuario',
        'nombre_completo',
        'rut',
        'correo_muni',
    ]