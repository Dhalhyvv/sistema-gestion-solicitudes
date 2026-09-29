from usuariosApp.models import Usuario
from solicitudesApp.models import Solicitud

for i in range(1, 6):
    Usuario.objects.filter(id_usuario="USR-00%d" % i).update(foto_perfil="img/usuario%d.svg" % i)

imagenes = {
    "SOL-001": "luminaria", "SOL-002": "taller", "SOL-003": "limpieza",
    "SOL-004": "limpieza", "SOL-005": "delegaciones", "SOL-006": "limpieza",
    "SOL-007": "equipo", "SOL-008": "taller", "SOL-009": "feria", "SOL-010": "taller",
}
for codigo, nombre in imagenes.items():
    Solicitud.objects.filter(id_solicitud=codigo).update(imagen_evidencia="img/%s.svg" % nombre)

print("Imagenes actualizadas")
