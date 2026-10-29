from django.conf import settings
from django.db import models
from django.utils import timezone

from usuariosApp.models import Usuario

ESTADOS_TRAMITE = ['Pendiente', 'En proceso', 'Realizado', 'Cancelado']
ESTADOS_CERRADOS = ('Realizado', 'Cancelado')
PRIORIDADES = ['Alta', 'Media', 'Baja']
IMAGENES_EVIDENCIA = [
    ('img/luminaria.svg', 'Luminaria / alumbrado'),
    ('img/limpieza.svg', 'Aseo y ornato'),
    ('img/taller.svg', 'Taller comunitario'),
    ('img/feria.svg', 'Feria / organizaciones'),
    ('img/delegaciones.svg', 'Delegación'),
]


class Delegacion(models.Model):
    """Mantenedor: delegaciones territoriales."""
    nombre = models.CharField(max_length=150, unique=True)
    descripcion = models.CharField(max_length=255, blank=True)
    activa = models.BooleanField(default=True)

    class Meta:
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Categoria(models.Model):
    """Mantenedor: categorías de solicitudes."""
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.CharField(max_length=255, blank=True)
    activa = models.BooleanField(default=True)

    class Meta:
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Solicitud(models.Model):
    """Mantenedor: solicitudes (tickets) vecinales."""
    id_solicitud = models.CharField(max_length=20, unique=True)
    fecha_registro = models.DateField()
    fecha_comprometida = models.DateField()
    delegacion = models.ForeignKey(
        Delegacion, on_delete=models.PROTECT, null=True, related_name='solicitudes')
    categoria = models.ForeignKey(
        Categoria, on_delete=models.PROTECT, null=True, related_name='solicitudes')
    descripcion_requerimiento = models.TextField()
    area_responsable = models.CharField(max_length=100)

    funcionario_responsable = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='solicitudes'
    )

    solicitante_muni = models.CharField(max_length=150)
    estado_tramite = models.CharField(max_length=50)
    nivel_prioridad = models.CharField(max_length=30)
    avance_porcentaje = models.PositiveIntegerField()
    imagen_evidencia = models.CharField(max_length=255)

    class Meta:
        ordering = ['-fecha_registro', '-id']

    def __str__(self):
        return self.id_solicitud

    @property
    def esta_abierta(self):
        return self.estado_tramite not in ESTADOS_CERRADOS

    @property
    def semaforo(self):
        """(color bootstrap, etiqueta) según estado y fecha comprometida."""
        if self.estado_tramite in ESTADOS_CERRADOS:
            return 'success', 'Cumplido'
        if not self.fecha_comprometida:
            return 'secondary', 'Sin fecha'
        dias = (self.fecha_comprometida - timezone.localdate()).days
        if dias < 0:
            return 'danger', 'Vencido'
        if dias <= 3:
            return 'warning', 'Próximo a vencer'
        return 'success', 'En plazo'

    @property
    def semaforo_color(self):
        return self.semaforo[0]

    @property
    def semaforo_etiqueta(self):
        return self.semaforo[1]


class AtencionSolicitud(models.Model):
    """TRANSACCIÓN: registro de atención sobre una solicitud.
    Relaciona Solicitud + Funcionario (Usuario) + cuenta que la registra (auth.User)
    y actualiza el estado/avance de la solicitud de forma atómica."""
    solicitud = models.ForeignKey(
        Solicitud, on_delete=models.CASCADE, related_name='atenciones')
    funcionario = models.ForeignKey(
        Usuario, on_delete=models.SET_NULL, null=True, related_name='atenciones')
    registrado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
        related_name='atenciones_registradas')
    fecha_hora = models.DateTimeField(auto_now_add=True)
    observacion = models.TextField()
    estado_anterior = models.CharField(max_length=50)
    estado_resultante = models.CharField(max_length=50)
    avance_anterior = models.PositiveIntegerField()
    avance_resultante = models.PositiveIntegerField()

    class Meta:
        ordering = ['-fecha_hora', '-id']

    def __str__(self):
        return f'Atención {self.solicitud.id_solicitud} ({self.fecha_hora:%d-%m-%Y %H:%M})'
