from django.contrib import admin
from .models import Usuario
from solicitudesApp.models import Solicitud


class SolicitudInline(admin.TabularInline):
    model = Solicitud
    extra = 0
    fields = ('id_solicitud', 'tipo_categoria', 'estado_tramite')
    show_change_link = True


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('id_usuario', 'nombre_completo', 'rut', 'rol', 'correo_muni', 'estado_cuenta')
    search_fields = ('id_usuario', 'nombre_completo', 'rut', 'correo_muni')
    list_filter = ('rol', 'estado_cuenta', 'delegacion_asignada')
    inlines = [SolicitudInline]
