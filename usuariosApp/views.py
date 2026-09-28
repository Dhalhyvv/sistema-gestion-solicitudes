import json
import os

from django.conf import settings
from django.shortcuts import render


def cargar_json(nombre_archivo):
    """Lee y retorna datos desde un archivo JSON en la carpeta data/."""
    ruta = os.path.join(settings.BASE_DIR, 'data', nombre_archivo)
    if os.path.exists(ruta):
        with open(ruta, 'r', encoding='utf-8') as archivo:
            return json.load(archivo)
    return []


def inicio_usuarios(request):
    usuarios = cargar_json('usuarios.json')
    roles = sorted({u.get('rol', 'Sin rol') for u in usuarios})
    delegaciones = sorted({u.get('delegacion_asignada', 'Sin delegación') for u in usuarios})

    contexto = {
        'titulo_modulo': 'Gestión de Usuarios y Roles Municipales',
        'total_usuarios': len(usuarios),
        'roles_disponibles': roles,
        'delegaciones': delegaciones,
    }
    return render(request, 'usuariosApp/inicio.html', contexto)


def lista_usuarios(request):
    usuarios = cargar_json('usuarios.json')
    activos = [u for u in usuarios if u.get('estado_cuenta') == 'Activo']
    administradores = [u for u in usuarios if 'Administrador' in u.get('rol', '')]

    contexto = {
        'usuarios': usuarios,
        'cantidad_activos': len(activos),
        'cantidad_administradores': len(administradores),
    }
    return render(request, 'usuariosApp/lista.html', contexto)
