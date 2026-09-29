from datetime import date
from usuariosApp.models import Usuario
from solicitudesApp.models import Solicitud

usuarios = [
    ("USR-001", "Carolina Muñoz Pérez", "12.345.678-5", "Jefa de Operaciones", "Centro", "cmunoz@muni.cl", "Activo"),
    ("USR-002", "Rodrigo Fuentes Silva", "13.456.789-0", "Inspector Municipal", "Norte", "rfuentes@muni.cl", "Activo"),
    ("USR-003", "Daniela Rojas Soto", "14.567.890-1", "Coordinadora Territorial", "Sur", "drojas@muni.cl", "Activo"),
    ("USR-004", "Felipe Araya Contreras", "15.678.901-2", "Encargado de Aseo y Ornato", "Oriente", "faraya@muni.cl", "Activo"),
    ("USR-005", "Valentina Castro Vera", "16.789.012-3", "Administrativa", "Poniente", "vcastro@muni.cl", "Inactivo"),
]

for u in usuarios:
    Usuario.objects.update_or_create(
        id_usuario=u[0],
        defaults={
            "nombre_completo": u[1], "rut": u[2], "rol": u[3],
            "delegacion_asignada": u[4], "correo_muni": u[5],
            "estado_cuenta": u[6], "foto_perfil": "usuarios/" + u[0].lower() + ".jpg",
        },
    )

solicitudes = [
    ("SOL-001", date(2026, 8, 3), date(2026, 8, 17), "Centro", "Alumbrado público", "Luminaria apagada en calle principal frente a la plaza.", "Alumbrado", "USR-001", "Juan Pérez", "En proceso", "Alta", 60),
    ("SOL-002", date(2026, 8, 5), date(2026, 8, 20), "Norte", "Bache en calzada", "Bache profundo que dificulta el paso de vehículos.", "Obras", "USR-002", "María González", "Pendiente", "Alta", 10),
    ("SOL-003", date(2026, 8, 7), date(2026, 8, 21), "Sur", "Retiro de escombros", "Acumulación de escombros en sitio eriazo.", "Aseo y Ornato", "USR-004", "Pedro Soto", "Realizado", "Media", 100),
    ("SOL-004", date(2026, 8, 10), date(2026, 8, 24), "Oriente", "Poda de árboles", "Ramas de árbol tocan el tendido eléctrico.", "Aseo y Ornato", "USR-004", "Ana Vergara", "En proceso", "Media", 45),
    ("SOL-005", date(2026, 8, 12), date(2026, 8, 26), "Poniente", "Ruidos molestos", "Denuncia por música a alto volumen en horario nocturno.", "Inspección", "USR-002", "Luis Tapia", "Pendiente", "Baja", 0),
    ("SOL-006", date(2026, 8, 14), date(2026, 8, 28), "Centro", "Basura acumulada", "Contenedores desbordados en esquina comercial.", "Aseo y Ornato", "USR-004", "Marta Ríos", "Realizado", "Media", 100),
    ("SOL-007", date(2026, 8, 18), date(2026, 9, 1), "Norte", "Señalética dañada", "Señal de tránsito caída en cruce escolar.", "Tránsito", "USR-003", "Jorge Núñez", "En proceso", "Alta", 70),
    ("SOL-008", date(2026, 8, 20), date(2026, 9, 3), "Sur", "Reparación de vereda", "Vereda rota con riesgo de caídas para adultos mayores.", "Obras", "USR-003", "Rosa Campos", "Pendiente", "Media", 15),
    ("SOL-009", date(2026, 8, 25), date(2026, 9, 8), "Oriente", "Perros abandonados", "Aviso por perros sin dueño en plaza del sector.", "Medio Ambiente", "USR-001", "Camilo Reyes", "Cancelado", "Baja", 0),
    ("SOL-010", date(2026, 9, 1), date(2026, 9, 15), "Poniente", "Filtración de agua", "Filtración en vía pública que genera pozas permanentes.", "Obras", "USR-002", "Sofía Paredes", "En proceso", "Alta", 35),
]

for s in solicitudes:
    Solicitud.objects.update_or_create(
        id_solicitud=s[0],
        defaults={
            "fecha_registro": s[1], "fecha_comprometida": s[2],
            "delegacion_territorial": s[3], "tipo_categoria": s[4],
            "descripcion_requerimiento": s[5], "area_responsable": s[6],
            "funcionario_responsable": Usuario.objects.get(id_usuario=s[7]),
            "solicitante_muni": s[8], "estado_tramite": s[9],
            "nivel_prioridad": s[10], "avance_porcentaje": s[11],
            "imagen_evidencia": "solicitudes/" + s[0].lower() + ".jpg",
        },
    )

print("Usuarios:", Usuario.objects.count(), "| Solicitudes:", Solicitud.objects.count())
