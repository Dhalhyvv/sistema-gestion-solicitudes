from django import forms
from django.utils import timezone

from usuariosApp.forms import BootstrapMixin
from usuariosApp.models import Usuario

from .models import (
    ESTADOS_CERRADOS, ESTADOS_TRAMITE, IMAGENES_EVIDENCIA, PRIORIDADES,
    Categoria, Delegacion, Solicitud,
)


def _choices(valores):
    return [(v, v) for v in valores]


class DelegacionForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = Delegacion
        fields = ['nombre', 'descripcion', 'activa']
        labels = {'nombre': 'Nombre de la delegación', 'descripcion': 'Descripción', 'activa': 'Activa'}

    def clean_nombre(self):
        nombre = ' '.join(self.cleaned_data['nombre'].split())
        if len(nombre) < 3:
            raise forms.ValidationError('El nombre debe tener al menos 3 caracteres.')
        if Delegacion.objects.filter(nombre__iexact=nombre).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Ya existe una delegación con ese nombre.')
        return nombre


class CategoriaForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nombre', 'descripcion', 'activa']
        labels = {'nombre': 'Nombre de la categoría', 'descripcion': 'Descripción', 'activa': 'Activa'}

    def clean_nombre(self):
        nombre = ' '.join(self.cleaned_data['nombre'].split())
        if len(nombre) < 3:
            raise forms.ValidationError('El nombre debe tener al menos 3 caracteres.')
        if Categoria.objects.filter(nombre__iexact=nombre).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Ya existe una categoría con ese nombre.')
        return nombre


class SolicitudForm(BootstrapMixin, forms.ModelForm):
    id_solicitud = forms.CharField(
        label='N° de solicitud', max_length=20, required=False,
        help_text='Déjelo vacío para generarlo automáticamente (SOL-AAAA-###).')
    fecha_registro = forms.DateField(
        label='Fecha de registro', initial=timezone.localdate,
        widget=forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'))
    fecha_comprometida = forms.DateField(
        label='Fecha comprometida',
        widget=forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'))
    delegacion = forms.ModelChoiceField(
        label='Delegación territorial', queryset=Delegacion.objects.none(), empty_label='Seleccione…')
    categoria = forms.ModelChoiceField(
        label='Categoría', queryset=Categoria.objects.none(), empty_label='Seleccione…')
    funcionario_responsable = forms.ModelChoiceField(
        label='Funcionario responsable', queryset=Usuario.objects.none(),
        required=False, empty_label='— Sin asignar —')
    estado_tramite = forms.ChoiceField(label='Estado del trámite', choices=_choices(ESTADOS_TRAMITE),
                                       initial='Pendiente')
    nivel_prioridad = forms.ChoiceField(label='Prioridad', choices=_choices(PRIORIDADES), initial='Media')
    avance_porcentaje = forms.IntegerField(
        label='Avance (%)', min_value=0, max_value=100, initial=0)
    imagen_evidencia = forms.ChoiceField(label='Imagen de evidencia', choices=IMAGENES_EVIDENCIA)

    class Meta:
        model = Solicitud
        fields = ['id_solicitud', 'fecha_registro', 'fecha_comprometida', 'delegacion', 'categoria',
                  'descripcion_requerimiento', 'area_responsable', 'funcionario_responsable',
                  'solicitante_muni', 'estado_tramite', 'nivel_prioridad', 'avance_porcentaje',
                  'imagen_evidencia']
        labels = {
            'descripcion_requerimiento': 'Descripción del requerimiento',
            'area_responsable': 'Área responsable',
            'solicitante_muni': 'Solicitante',
        }
        widgets = {'descripcion_requerimiento': forms.Textarea(attrs={'rows': 4})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Solo catálogos vigentes (más el valor actual si se está editando)
        deleg = Delegacion.objects.filter(activa=True)
        cat = Categoria.objects.filter(activa=True)
        if self.instance.pk:
            if self.instance.delegacion_id:
                deleg = Delegacion.objects.filter(activa=True) | Delegacion.objects.filter(pk=self.instance.delegacion_id)
            if self.instance.categoria_id:
                cat = Categoria.objects.filter(activa=True) | Categoria.objects.filter(pk=self.instance.categoria_id)
        self.fields['delegacion'].queryset = deleg.distinct()
        self.fields['categoria'].queryset = cat.distinct()
        self.fields['funcionario_responsable'].queryset = Usuario.objects.filter(estado_cuenta='Activo')
        self._estilizar()

    def clean_id_solicitud(self):
        codigo = self.cleaned_data.get('id_solicitud', '').strip().upper()
        if codigo and Solicitud.objects.filter(id_solicitud=codigo).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Ese número de solicitud ya existe.')
        return codigo

    def clean(self):
        datos = super().clean()
        registro, comprometida = datos.get('fecha_registro'), datos.get('fecha_comprometida')
        if registro and comprometida and comprometida < registro:
            self.add_error('fecha_comprometida', 'La fecha comprometida no puede ser anterior a la de registro.')
        estado, avance = datos.get('estado_tramite'), datos.get('avance_porcentaje')
        if estado == 'Realizado' and avance is not None and avance != 100:
            self.add_error('avance_porcentaje', 'Una solicitud realizada debe tener 100% de avance.')
        if estado == 'Pendiente' and avance:
            self.add_error('avance_porcentaje', 'Una solicitud pendiente no puede tener avance mayor a 0%.')
        return datos

    def save(self, commit=True):
        obj = super().save(commit=False)
        if not obj.id_solicitud:
            anio = timezone.localdate().year
            n = Solicitud.objects.filter(id_solicitud__startswith=f'SOL-{anio}-').count() + 1
            while Solicitud.objects.filter(id_solicitud=f'SOL-{anio}-{n:03d}').exists():
                n += 1
            obj.id_solicitud = f'SOL-{anio}-{n:03d}'
        if commit:
            obj.save()
        return obj


class AtencionForm(BootstrapMixin, forms.Form):
    """Formulario de la TRANSACCIÓN: registrar atención de una solicitud."""
    solicitud = forms.ModelChoiceField(
        label='Solicitud', queryset=Solicitud.objects.none(), empty_label='Seleccione una solicitud…')
    funcionario = forms.ModelChoiceField(
        label='Funcionario que atiende', queryset=Usuario.objects.none(), empty_label='Seleccione…')
    estado_resultante = forms.ChoiceField(label='Nuevo estado', choices=_choices(ESTADOS_TRAMITE))
    avance_resultante = forms.IntegerField(label='Nuevo avance (%)', min_value=0, max_value=100)
    observacion = forms.CharField(
        label='Observación de la atención', widget=forms.Textarea(attrs={'rows': 4}),
        help_text='Describa qué se realizó (mínimo 10 caracteres).')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['solicitud'].queryset = Solicitud.objects.exclude(
            estado_tramite__in=ESTADOS_CERRADOS).select_related('delegacion')
        self.fields['funcionario'].queryset = Usuario.objects.filter(estado_cuenta='Activo')
        self._estilizar()

    def clean_observacion(self):
        texto = self.cleaned_data['observacion'].strip()
        if len(texto) < 10:
            raise forms.ValidationError('La observación debe tener al menos 10 caracteres.')
        return texto

    def clean(self):
        datos = super().clean()
        sol = datos.get('solicitud')
        estado, avance = datos.get('estado_resultante'), datos.get('avance_resultante')
        if sol and avance is not None:
            if avance < sol.avance_porcentaje:
                self.add_error('avance_resultante',
                               f'El avance no puede ser menor al actual ({sol.avance_porcentaje}%).')
            if estado == 'Realizado' and avance != 100:
                self.add_error('avance_resultante', 'Para marcar como Realizado el avance debe ser 100%.')
            if avance == 100 and estado not in ('Realizado', 'Cancelado'):
                self.add_error('estado_resultante', 'Con 100% de avance el estado debe ser Realizado.')
            if estado == 'Pendiente' and avance > 0:
                self.add_error('estado_resultante', 'Con avance mayor a 0% el estado no puede ser Pendiente.')
        return datos
