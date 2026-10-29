from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.generic import DetailView

from usuariosApp.mixins import (
    CrearMixin, EditarMixin, EliminarMixin, ListaMixin, PermisoModeloMixin,
)

from .forms import AtencionForm, CategoriaForm, DelegacionForm, SolicitudForm
from .models import (
    ESTADOS_CERRADOS, ESTADOS_TRAMITE, PRIORIDADES,
    AtencionSolicitud, Categoria, Delegacion, Solicitud,
)
from .services import registrar_atencion


def _si_no(valor):
    return 'Sí' if valor else 'No'


# ------------------------------------------------------- Mantenedor: Delegaciones
class DelegacionLista(ListaMixin):
    model = Delegacion
    titulo = 'Delegaciones territoriales'
    search_fields = ['nombre', 'descripcion']
    columnas = [('Nombre', 'nombre'), ('Descripción', 'descripcion'),
                ('Activa', lambda o: _si_no(o.activa)),
                ('Solicitudes', lambda o: o.solicitudes.count())]
    url_nuevo, url_editar, url_eliminar = 'delegacion_crear', 'delegacion_editar', 'delegacion_eliminar'
    etiqueta_nuevo = 'Nueva delegación'


class DelegacionCrear(CrearMixin):
    model = Delegacion
    form_class = DelegacionForm
    titulo = 'Nueva delegación'
    url_lista = 'delegacion_lista'
    mensaje_ok = 'Delegación creada correctamente.'


class DelegacionEditar(EditarMixin):
    model = Delegacion
    form_class = DelegacionForm
    titulo = 'Editar delegación'
    url_lista = 'delegacion_lista'
    mensaje_ok = 'Delegación actualizada correctamente.'


class DelegacionEliminar(EliminarMixin):
    model = Delegacion
    titulo = 'Eliminar delegación'
    url_lista = 'delegacion_lista'


# -------------------------------------------------------- Mantenedor: Categorías
class CategoriaLista(ListaMixin):
    model = Categoria
    titulo = 'Categorías de solicitudes'
    search_fields = ['nombre', 'descripcion']
    columnas = [('Nombre', 'nombre'), ('Descripción', 'descripcion'),
                ('Activa', lambda o: _si_no(o.activa)),
                ('Solicitudes', lambda o: o.solicitudes.count())]
    url_nuevo, url_editar, url_eliminar = 'categoria_crear', 'categoria_editar', 'categoria_eliminar'
    etiqueta_nuevo = 'Nueva categoría'


class CategoriaCrear(CrearMixin):
    model = Categoria
    form_class = CategoriaForm
    titulo = 'Nueva categoría'
    url_lista = 'categoria_lista'
    mensaje_ok = 'Categoría creada correctamente.'


class CategoriaEditar(EditarMixin):
    model = Categoria
    form_class = CategoriaForm
    titulo = 'Editar categoría'
    url_lista = 'categoria_lista'
    mensaje_ok = 'Categoría actualizada correctamente.'


class CategoriaEliminar(EliminarMixin):
    model = Categoria
    titulo = 'Eliminar categoría'
    url_lista = 'categoria_lista'


# -------------------------------------------------------- Mantenedor: Solicitudes
class SolicitudLista(ListaMixin):
    model = Solicitud
    template_name = 'solicitudesApp/lista.html'
    titulo = 'Solicitudes territoriales (tickets)'
    search_fields = ['id_solicitud', 'descripcion_requerimiento', 'solicitante_muni',
                     'delegacion__nombre', 'categoria__nombre', 'funcionario_responsable__nombre_completo']
    columnas = [('N°', 'id_solicitud'), ('Categoría', 'categoria'), ('Delegación', 'delegacion'),
                ('Responsable', 'funcionario_responsable'), ('Prioridad', 'nivel_prioridad'),
                ('Estado', 'estado_tramite'), ('Avance', lambda o: f'{o.avance_porcentaje}%'),
                ('Compromiso', lambda o: o.fecha_comprometida.strftime('%d-%m-%Y'))]
    url_nuevo, url_editar, url_eliminar = 'solicitud_crear', 'solicitud_editar', 'solicitud_eliminar'
    url_detalle = 'solicitud_detalle'
    etiqueta_nuevo = 'Nueva solicitud'

    def get_queryset(self):
        qs = super().get_queryset().select_related('delegacion', 'categoria', 'funcionario_responsable')
        estado = self.request.GET.get('estado', '')
        prioridad = self.request.GET.get('prioridad', '')
        if estado in ESTADOS_TRAMITE:
            qs = qs.filter(estado_tramite=estado)
        if prioridad in PRIORIDADES:
            qs = qs.filter(nivel_prioridad=prioridad)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        semaforos = {o.pk: o.semaforo for o in ctx['object_list']}
        ctx['filas'] = [(o, v, semaforos[o.pk]) for o, v in ctx['filas']]
        ctx.update({
            'estados': ESTADOS_TRAMITE, 'prioridades': PRIORIDADES,
            'estado_sel': self.request.GET.get('estado', ''),
            'prioridad_sel': self.request.GET.get('prioridad', ''),
            'puede_atender': self.request.user.has_perm('solicitudesApp.add_atencionsolicitud'),
        })
        return ctx


class SolicitudDetalle(PermisoModeloMixin, DetailView):
    model = Solicitud
    template_name = 'solicitudesApp/detalle.html'
    accion = 'view'

    def get_queryset(self):
        return super().get_queryset().select_related(
            'delegacion', 'categoria', 'funcionario_responsable')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['atenciones'] = self.object.atenciones.select_related('funcionario', 'registrado_por')
        ctx['puede_atender'] = (self.request.user.has_perm('solicitudesApp.add_atencionsolicitud')
                                and self.object.esta_abierta)
        return ctx


class SolicitudCrear(CrearMixin):
    model = Solicitud
    form_class = SolicitudForm
    titulo = 'Nueva solicitud'
    url_lista = 'solicitud_lista'
    mensaje_ok = 'Solicitud registrada correctamente.'


class SolicitudEditar(EditarMixin):
    model = Solicitud
    form_class = SolicitudForm
    titulo = 'Editar solicitud'
    url_lista = 'solicitud_lista'
    mensaje_ok = 'Solicitud actualizada correctamente.'


class SolicitudEliminar(EliminarMixin):
    model = Solicitud
    titulo = 'Eliminar solicitud'
    url_lista = 'solicitud_lista'


# ----------------------------------------------------- TRANSACCIÓN: Atenciones
class AtencionLista(ListaMixin):
    model = AtencionSolicitud
    titulo = 'Historial de atenciones'
    search_fields = ['solicitud__id_solicitud', 'observacion', 'funcionario__nombre_completo',
                     'registrado_por__username']
    columnas = [('Fecha', lambda o: timezone.localtime(o.fecha_hora).strftime('%d-%m-%Y %H:%M')),
                ('Solicitud', 'solicitud'), ('Funcionario', 'funcionario'),
                ('Estado', lambda o: f'{o.estado_anterior} → {o.estado_resultante}'),
                ('Avance', lambda o: f'{o.avance_anterior}% → {o.avance_resultante}%'),
                ('Registrado por', 'registrado_por'), ('Observación', 'observacion')]
    url_nuevo = 'atencion_nueva'
    etiqueta_nuevo = 'Registrar atención'

    def get_queryset(self):
        return super().get_queryset().select_related('solicitud', 'funcionario', 'registrado_por')


@login_required
@permission_required('solicitudesApp.add_atencionsolicitud', raise_exception=True)
def atencion_nueva(request, pk=None):
    """Registra una atención: crea AtencionSolicitud y actualiza la Solicitud (transacción atómica)."""
    solicitud = get_object_or_404(Solicitud, pk=pk) if pk else None
    if solicitud and not solicitud.esta_abierta:
        messages.warning(request, f'La solicitud {solicitud.id_solicitud} ya está cerrada ({solicitud.estado_tramite}).')
        return redirect('solicitud_detalle', pk=solicitud.pk)

    if request.method == 'POST':
        form = AtencionForm(request.POST)
        if form.is_valid():
            d = form.cleaned_data
            registrar_atencion(
                solicitud_id=d['solicitud'].pk, funcionario=d['funcionario'], usuario=request.user,
                observacion=d['observacion'], estado=d['estado_resultante'], avance=d['avance_resultante'])
            messages.success(
                request, f'Atención registrada. La solicitud {d["solicitud"].id_solicitud} '
                         f'quedó en estado «{d["estado_resultante"]}» con {d["avance_resultante"]}% de avance.')
            return redirect('solicitud_detalle', pk=d['solicitud'].pk)
    else:
        initial = {}
        if solicitud:
            initial = {'solicitud': solicitud, 'estado_resultante': solicitud.estado_tramite,
                       'avance_resultante': solicitud.avance_porcentaje,
                       'funcionario': solicitud.funcionario_responsable}
        form = AtencionForm(initial=initial)
    return render(request, 'solicitudesApp/atencion_form.html', {
        'form': form, 'solicitud': solicitud, 'titulo': 'Registrar atención de solicitud'})
