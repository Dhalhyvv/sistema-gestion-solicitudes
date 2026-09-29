from django.contrib import admin
from .models import Solicitud


@admin.register(Solicitud)
class SolicitudAdmin(admin.ModelAdmin):
    list_display = (
        'id_solicitud',
        'fecha_registro',
        'tipo_categoria',
        'funcionario_responsable',
        'estado_tramite',
        'nivel_prioridad',
        'avance_porcentaje',
    )
    search_fields = (
        'id_solicitud',
        'descripcion_requerimiento',
        'solicitante_muni',
        'funcionario_responsable__nombre_completo',
    )
    list_filter = (
        'estado_tramite',
        'nivel_prioridad',
        'tipo_categoria',
        'delegacion_territorial',
    )
    date_hierarchy = 'fecha_registro'
