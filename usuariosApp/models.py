from django.conf import settings
from django.db import models

ROLES_FUNCIONARIO = [
    'Funcionario', 'Delegado', 'Supervisor',
    'Administrador del sistema', 'Usuario de consulta',
]
ESTADOS_CUENTA = ['Activo', 'Inactivo']
FOTOS_PERFIL = [f'img/usuario{i}.svg' for i in range(1, 6)]


class Usuario(models.Model):
    """Personal municipal (mantenedor de Funcionarios).
    Puede vincularse opcionalmente con una cuenta de acceso (auth.User)."""
    id_usuario = models.CharField(max_length=20, unique=True)
    nombre_completo = models.CharField(max_length=150)
    rut = models.CharField(max_length=20, unique=True)
    rol = models.CharField(max_length=100)
    delegacion_asignada = models.CharField(max_length=150)
    correo_muni = models.EmailField(max_length=150, unique=True)
    estado_cuenta = models.CharField(max_length=30)
    foto_perfil = models.CharField(max_length=255)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='funcionario',
    )

    class Meta:
        ordering = ['nombre_completo']

    def __str__(self):
        return self.nombre_completo
