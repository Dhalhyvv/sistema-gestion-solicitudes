from django.db import models

# Create your models here.
from django.db import models


class Usuario(models.Model):
    id_usuario = models.CharField(max_length=20, unique=True)
    nombre_completo = models.CharField(max_length=150)
    rut = models.CharField(max_length=20, unique=True)
    rol = models.CharField(max_length=100)
    delegacion_asignada = models.CharField(max_length=150)
    correo_muni = models.EmailField(max_length=150, unique=True)
    estado_cuenta = models.CharField(max_length=30)
    foto_perfil = models.CharField(max_length=255)

    def __str__(self):
        return self.nombre_completo