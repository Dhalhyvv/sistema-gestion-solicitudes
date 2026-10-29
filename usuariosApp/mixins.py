"""Bloques reutilizables para los mantenedores (CRUD) basados en Django Templates."""
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import ProtectedError, Q
from django.shortcuts import redirect
from django.views.generic import CreateView, DeleteView, ListView, UpdateView


class PermisoModeloMixin(PermissionRequiredMixin):
    """Exige el permiso Django <app>.<accion>_<modelo>. Sin sesión -> login; sin permiso -> 403."""
    accion = 'view'

    def get_permission_required(self):
        meta = self.model._meta
        return [f'{meta.app_label}.{self.accion}_{meta.model_name}']


class ListaMixin(PermisoModeloMixin, ListView):
    """Listado con búsqueda (?q=) y paginación. Las columnas se declaran en la vista."""
    accion = 'view'
    template_name = 'crud/lista.html'
    paginate_by = 10
    search_fields = []
    columnas = []            # [(titulo, 'atributo' | callable)]
    titulo = ''
    url_nuevo = ''           # nombre de URL (vacío = sin botón)
    url_editar = ''
    url_eliminar = ''
    url_detalle = ''
    etiqueta_nuevo = 'Nuevo registro'

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get('q', '').strip()
        if q and self.search_fields:
            condicion = Q()
            for campo in self.search_fields:
                condicion |= Q(**{f'{campo}__icontains': q})
            qs = qs.filter(condicion)
        return qs

    @staticmethod
    def _valor(obj, origen):
        valor = origen(obj) if callable(origen) else getattr(obj, origen, '')
        return '—' if valor in (None, '') else valor

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        meta = self.model._meta
        user = self.request.user
        params = self.request.GET.copy()
        params.pop('page', None)
        ctx.update({
            'titulo': self.titulo,
            'encabezados': [c[0] for c in self.columnas],
            'filas': [(o, [self._valor(o, c[1]) for c in self.columnas]) for o in ctx['object_list']],
            'q': self.request.GET.get('q', ''),
            'qs': params.urlencode(),
            'url_nuevo': self.url_nuevo,
            'url_editar': self.url_editar,
            'url_eliminar': self.url_eliminar,
            'url_detalle': self.url_detalle,
            'etiqueta_nuevo': self.etiqueta_nuevo,
            'puede_crear': bool(self.url_nuevo) and user.has_perm(f'{meta.app_label}.add_{meta.model_name}'),
            'puede_editar': bool(self.url_editar) and user.has_perm(f'{meta.app_label}.change_{meta.model_name}'),
            'puede_eliminar': bool(self.url_eliminar) and user.has_perm(f'{meta.app_label}.delete_{meta.model_name}'),
            'total': ctx['paginator'].count,
        })
        return ctx


class _FormularioBase(PermisoModeloMixin):
    template_name = 'crud/form.html'
    titulo = ''
    url_lista = ''
    mensaje_ok = ''

    def get_success_url(self):
        from django.urls import reverse
        return reverse(self.url_lista)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update({'titulo': self.titulo, 'url_lista': self.url_lista})
        return ctx

    def form_valid(self, form):
        respuesta = super().form_valid(form)
        if self.mensaje_ok:
            messages.success(self.request, self.mensaje_ok)
        return respuesta


class CrearMixin(_FormularioBase, CreateView):
    accion = 'add'


class EditarMixin(_FormularioBase, UpdateView):
    accion = 'change'


class EliminarMixin(PermisoModeloMixin, DeleteView):
    accion = 'delete'
    template_name = 'crud/confirmar_eliminar.html'
    titulo = ''
    url_lista = ''

    def get_success_url(self):
        from django.urls import reverse
        return reverse(self.url_lista)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update({'titulo': self.titulo, 'url_lista': self.url_lista})
        return ctx

    def puede_eliminar(self):
        """Hook para reglas extra; devuelve (bool, mensaje)."""
        return True, ''

    def form_valid(self, form):
        self.object = self.get_object()
        ok, motivo = self.puede_eliminar()
        if not ok:
            messages.error(self.request, motivo)
            return redirect(self.get_success_url())
        try:
            nombre = str(self.object)
            self.object.delete()
        except ProtectedError:
            messages.error(
                self.request,
                f'No se puede eliminar «{self.object}» porque tiene registros asociados.')
            return redirect(self.get_success_url())
        messages.success(self.request, f'«{nombre}» fue eliminado correctamente.')
        return redirect(self.get_success_url())
