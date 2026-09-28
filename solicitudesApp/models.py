from django.db import models

# Create your models here.
from django.db import models
from usuariosApp.models import Usuario


class Solicitud(models.Model):
    id_solicitud = models.CharField(max_length=20, unique=True)
    fecha_registro = models.DateField()
    fecha_comprometida = models.DateField()
    delegacion_territorial = models.CharField(max_length=150)
    tipo_categoria = models.CharField(max_length=100)
    descripcion_requerimiento = models.TextField()
    area_responsable = models.CharField(max_length=100)

    funcionario_responsable = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        related_name='solicitudes'
    )

    solicitante_muni = models.CharField(max_length=150)
    estado_tramite = models.CharField(max_length=50)
    nivel_prioridad = models.CharField(max_length=30)
    avance_porcentaje = models.PositiveIntegerField()
    imagen_evidencia = models.CharField(max_length=255)

    def __str__(self):
        return self.id_solicitud