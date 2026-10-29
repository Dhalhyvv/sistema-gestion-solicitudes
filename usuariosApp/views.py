from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.shortcuts import render
from django.utils import timezone

from solicitudesApp.models import (
    ESTADOS_CERRADOS, AtencionSolicitud, Categoria, Delegacion, Solicitud,
)

from .forms import CuentaCrearForm, CuentaEditarForm, FuncionarioForm, LoginForm
from .mixins import CrearMixin, EditarMixin, EliminarMixin, ListaMixin
from .models import Usuario
from .perfiles import ADMINISTRADOR, SUPERVISOR, obtener_perfil


# ---------------------------------------------------------------- Autenticación
class LoginView(auth_views.LoginView):
    template_name = 'registration/login.html'
    authentication_form = LoginForm
    redirect_authenticated_user = True


def error_403(request, exception=None):
    return render(request, '403.html', status=403)


# ------------------------------------------------------------------- Dashboards
def _resumen_solicitudes():
    hoy = timezone.localdate()
    abiertas = Solicitud.objects.exclude(estado_tramite__in=ESTADOS_CERRADOS)
    por_estado = {e['estado_tramite']: e['n'] for e in
                  Solicitud.objects.values('estado_tramite').annotate(n=Count('id'))}
    total = Solicitud.objects.count()
    return {
        'hoy': hoy,
        'total_solicitudes': total,
        'pendientes': por_estado.get('Pendiente', 0),
        'en_proceso': por_estado.get('En proceso', 0),
        'realizadas': por_estado.get('Realizado', 0),
        'canceladas': por_estado.get('Cancelado', 0),
        'vencidas': abiertas.filter(fecha_comprometida__lt=hoy).count(),
        'urgentes': abiertas.filter(nivel_prioridad='Alta').count(),
        'avance_promedio': round(sum(Solicitud.objects.values_list('avance_porcentaje', flat=True)) / total) if total else 0,
    }


@login_required
def dashboard(request):
    """Un único punto de entrada: el contenido cambia según el perfil autenticado."""
    perfil = obtener_perfil(request.user)
    if perfil is None:
        return render(request, 'usuariosApp/dashboard_sin_perfil.html', status=403)

    ctx = _resumen_solicitudes()
    ctx['perfil'] = perfil
    ultimas = AtencionSolicitud.objects.select_related('solicitud', 'funcionario', 'registrado_por')

    if perfil == ADMINISTRADOR:
        ctx.update({
            'total_funcionarios': Usuario.objects.count(),
            'total_delegaciones': Delegacion.objects.count(),
            'total_categorias': Categoria.objects.count(),
            'total_cuentas': User.objects.count(),
            'cuentas_activas': User.objects.filter(is_active=True).count(),
            'total_atenciones': AtencionSolicitud.objects.count(),
            'cuentas_por_perfil': User.objects.values('groups__name').annotate(n=Count('id', distinct=True)).order_by('groups__name'),
            'por_delegacion': Delegacion.objects.annotate(n=Count('solicitudes')).order_by('-n', 'nombre'),
            'por_categoria': Categoria.objects.annotate(n=Count('solicitudes')).order_by('-n', 'nombre'),
            'ultimas_atenciones': ultimas[:6],
            'ultimas_cuentas': User.objects.order_by('-date_joined')[:5],
        })
        plantilla = 'usuariosApp/dashboard_admin.html'
    elif perfil == SUPERVISOR:
        abiertas = Solicitud.objects.exclude(estado_tramite__in=ESTADOS_CERRADOS)
        ctx.update({
            'por_delegacion': Delegacion.objects.annotate(
                n=Count('solicitudes', filter=~Q(solicitudes__estado_tramite__in=ESTADOS_CERRADOS))
            ).order_by('-n', 'nombre'),
            'criticas': abiertas.select_related('delegacion', 'categoria', 'funcionario_responsable')
                                 .filter(Q(fecha_comprometida__lt=ctx['hoy']) | Q(nivel_prioridad='Alta'))
                                 .order_by('fecha_comprometida')[:6],
            'ultimas_atenciones': ultimas[:6],
        })
        plantilla = 'usuariosApp/dashboard_supervisor.html'
    else:
        funcionario = getattr(request.user, 'funcionario', None)
        mias = Solicitud.objects.select_related('delegacion', 'categoria').exclude(
            estado_tramite__in=ESTADOS_CERRADOS)
        if funcionario:
            mias = mias.filter(funcionario_responsable=funcionario)
        ctx.update({
            'funcionario': funcionario,
            'mis_solicitudes': mias.order_by('fecha_comprometida')[:8],
            'mis_atenciones': ultimas.filter(registrado_por=request.user)[:5],
        })
        plantilla = 'usuariosApp/dashboard_administrativo.html'
    return render(request, plantilla, ctx)


# -------------------------------------------- Mantenedor: Funcionarios (personal)
class FuncionarioLista(ListaMixin):
    model = Usuario
    titulo = 'Funcionarios municipales'
    search_fields = ['id_usuario', 'nombre_completo', 'rut', 'correo_muni', 'rol', 'delegacion_asignada']
    columnas = [('ID', 'id_usuario'), ('Nombre', 'nombre_completo'), ('RUT', 'rut'),
                ('Rol', 'rol'), ('Delegación', 'delegacion_asignada'),
                ('Correo', 'correo_muni'), ('Estado', 'estado_cuenta')]
    url_nuevo, url_editar, url_eliminar = 'funcionario_crear', 'funcionario_editar', 'funcionario_eliminar'
    etiqueta_nuevo = 'Nuevo funcionario'


class FuncionarioCrear(CrearMixin):
    model = Usuario
    form_class = FuncionarioForm
    titulo = 'Nuevo funcionario'
    url_lista = 'funcionario_lista'
    mensaje_ok = 'Funcionario creado correctamente.'


class FuncionarioEditar(EditarMixin):
    model = Usuario
    form_class = FuncionarioForm
    titulo = 'Editar funcionario'
    url_lista = 'funcionario_lista'
    mensaje_ok = 'Funcionario actualizado correctamente.'


class FuncionarioEliminar(EliminarMixin):
    model = Usuario
    titulo = 'Eliminar funcionario'
    url_lista = 'funcionario_lista'


# ---------------------------------- Gestión de usuarios del sistema (solo Admin)
class CuentaLista(ListaMixin):
    model = User
    titulo = 'Usuarios del sistema'
    search_fields = ['username', 'first_name', 'last_name', 'email', 'groups__name']
    columnas = [('Usuario', 'username'),
                ('Nombre', lambda u: u.get_full_name()),
                ('Correo', 'email'),
                ('Perfil', lambda u: obtener_perfil(u) or 'Sin perfil'),
                ('Estado', lambda u: 'Activo' if u.is_active else 'Inactivo'),
                ('Último acceso', lambda u: u.last_login.strftime('%d-%m-%Y %H:%M') if u.last_login else 'Nunca')]
    url_nuevo, url_editar, url_eliminar = 'cuenta_crear', 'cuenta_editar', 'cuenta_eliminar'
    etiqueta_nuevo = 'Nuevo usuario'

    def get_queryset(self):
        return super().get_queryset().prefetch_related('groups').distinct().order_by('username')


class CuentaCrear(CrearMixin):
    model = User
    form_class = CuentaCrearForm
    titulo = 'Nuevo usuario del sistema'
    url_lista = 'cuenta_lista'
    mensaje_ok = 'Usuario creado y perfil asignado correctamente.'


class CuentaEditar(EditarMixin):
    model = User
    form_class = CuentaEditarForm
    titulo = 'Editar usuario del sistema'
    url_lista = 'cuenta_lista'
    mensaje_ok = 'Usuario actualizado correctamente.'


class CuentaEliminar(EliminarMixin):
    model = User
    titulo = 'Eliminar usuario del sistema'
    url_lista = 'cuenta_lista'

    def puede_eliminar(self):
        if self.object.pk == self.request.user.pk:
            return False, 'No puede eliminar su propia cuenta mientras está conectado.'
        if self.object.is_superuser and User.objects.filter(is_superuser=True).count() == 1:
            return False, 'No se puede eliminar el único superusuario del sistema.'
        return True, ''
