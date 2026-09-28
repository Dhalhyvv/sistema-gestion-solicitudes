from datetime import datetime

from django.shortcuts import render
from .models import Solicitud


def calcular_semaforo(fecha_comprometida, estado_tramite):
    """Determina el color del semáforo según estado y fecha comprometida."""
    if estado_tramite in ('Realizado', 'Cancelado'):
        return 'success', 'Cumplido'

    if not fecha_comprometida:
        return 'secondary', 'Sin fecha'

    hoy = datetime.now().date()
    dias_restantes = (fecha_comprometida - hoy).days

    if dias_restantes < 0:
        return 'danger', 'Vencido'
    if dias_restantes <= 3:
        return 'warning', 'Próximo a vencer'
    return 'success', 'En plazo'


def inicio_solicitudes(request):
    resumen = Solicitud.objects.all()
    total = len(resumen)
    pendientes = sum(1 for s in resumen if s.estado_tramite == 'Pendiente')
    en_proceso = sum(1 for s in resumen if s.estado_tramite == 'En proceso')
    realizadas = sum(1 for s in resumen if s.estado_tramite == 'Realizado')

    contexto = {
        'titulo_modulo': 'Sistema de Seguimiento de Solicitudes Vecinales',
        'total_solicitudes': total,
        'pendientes': pendientes,
        'en_proceso': en_proceso,
        'realizadas': realizadas,
    }
    return render(request, 'solicitudesApp/inicio.html', contexto)


def lista_solicitudes(request):
    solicitudes = Solicitud.objects.all()

    for solicitud in solicitudes:
        color, etiqueta = calcular_semaforo(
            solicitud.fecha_comprometida,
            solicitud.estado_tramite,
        )
        solicitud.semaforo_color = color
        solicitud.semaforo_etiqueta = etiqueta

    urgentes = [s for s in solicitudes if s.nivel_prioridad == 'Alta']
    vencidas = [s for s in solicitudes if s.semaforo_etiqueta == 'Vencido']

    contexto = {
        'solicitudes': solicitudes,
        'cantidad_urgentes': len(urgentes),
        'cantidad_vencidas': len(vencidas),
    }
    return render(request, 'solicitudesApp/lista.html', contexto)
