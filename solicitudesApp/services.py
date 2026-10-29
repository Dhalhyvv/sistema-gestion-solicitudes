from django.db import transaction

from .models import AtencionSolicitud, Solicitud


@transaction.atomic
def registrar_atencion(solicitud_id, funcionario, usuario, observacion, estado, avance):
    """Transacción: crea la atención y actualiza la solicitud en una sola operación atómica.
    Si algo falla, no queda ningún cambio a medias en la base de datos."""
    solicitud = Solicitud.objects.select_for_update().get(pk=solicitud_id)
    atencion = AtencionSolicitud.objects.create(
        solicitud=solicitud,
        funcionario=funcionario,
        registrado_por=usuario,
        observacion=observacion,
        estado_anterior=solicitud.estado_tramite,
        estado_resultante=estado,
        avance_anterior=solicitud.avance_porcentaje,
        avance_resultante=avance,
    )
    solicitud.estado_tramite = estado
    solicitud.avance_porcentaje = avance
    solicitud.funcionario_responsable = funcionario
    solicitud.save(update_fields=['estado_tramite', 'avance_porcentaje', 'funcionario_responsable'])
    return atencion
