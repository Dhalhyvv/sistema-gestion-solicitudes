from django.shortcuts import render
from .models import Usuario


def inicio_usuarios(request):
    contexto = {
        'titulo_modulo': 'Gestión de Usuarios y Roles Municipales',
        'total_usuarios': Usuario.objects.count(),
        'roles_disponibles': Usuario.objects.order_by('rol').values_list('rol', flat=True).distinct(),
        'delegaciones': Usuario.objects.order_by('delegacion_asignada').values_list('delegacion_asignada', flat=True).distinct(),
    }
    return render(request, 'usuariosApp/inicio.html', contexto)


def lista_usuarios(request):
    contexto = {
        'usuarios': Usuario.objects.all(),
        'cantidad_activos': Usuario.objects.filter(estado_cuenta='Activo').count(),
        'cantidad_administradores': Usuario.objects.filter(rol__icontains='Administrador').count(),
    }
    return render(request, 'usuariosApp/lista.html', contexto)
