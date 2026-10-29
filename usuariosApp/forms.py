from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import Group, User

from .models import ESTADOS_CUENTA, FOTOS_PERFIL, ROLES_FUNCIONARIO, Usuario
from .validators import normalizar_rut


class BootstrapMixin:
    """Aplica clases Bootstrap a todos los campos y marca los inválidos."""

    def _estilizar(self):
        for campo in self.fields.values():
            w = campo.widget
            if isinstance(w, forms.CheckboxInput):
                w.attrs['class'] = 'form-check-input'
            elif isinstance(w, (forms.Select, forms.SelectMultiple)):
                w.attrs['class'] = 'form-select'
            else:
                w.attrs['class'] = 'form-control'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._estilizar()

    def full_clean(self):
        super().full_clean()
        for nombre in self.errors:
            if nombre in self.fields:
                w = self.fields[nombre].widget
                w.attrs['class'] = w.attrs.get('class', '') + ' is-invalid'


def _choices(valores):
    return [(v, v) for v in valores]


class LoginForm(BootstrapMixin, AuthenticationForm):
    username = forms.CharField(label='Usuario', widget=forms.TextInput(attrs={'autofocus': True}))
    password = forms.CharField(label='Contraseña', strip=False, widget=forms.PasswordInput)


class FuncionarioForm(BootstrapMixin, forms.ModelForm):
    id_usuario = forms.CharField(
        label='ID de funcionario', max_length=20, required=False,
        help_text='Déjelo vacío para generarlo automáticamente (USR-###).')
    rol = forms.ChoiceField(label='Rol', choices=_choices(ROLES_FUNCIONARIO))
    estado_cuenta = forms.ChoiceField(label='Estado', choices=_choices(ESTADOS_CUENTA))
    foto_perfil = forms.ChoiceField(
        label='Avatar', choices=[(f, f.split('/')[-1].replace('.svg', '').capitalize()) for f in FOTOS_PERFIL])

    class Meta:
        model = Usuario
        fields = ['id_usuario', 'nombre_completo', 'rut', 'rol', 'delegacion_asignada',
                  'correo_muni', 'estado_cuenta', 'foto_perfil']
        labels = {
            'nombre_completo': 'Nombre completo',
            'rut': 'RUT',
            'delegacion_asignada': 'Delegación asignada',
            'correo_muni': 'Correo municipal',
        }

    def clean_nombre_completo(self):
        nombre = ' '.join(self.cleaned_data['nombre_completo'].split())
        if len(nombre) < 5 or ' ' not in nombre:
            raise forms.ValidationError('Ingrese nombre y apellido.')
        return nombre

    def clean_rut(self):
        rut = normalizar_rut(self.cleaned_data['rut'])
        qs = Usuario.objects.filter(rut=rut).exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('Ya existe un funcionario con este RUT.')
        return rut

    def clean_correo_muni(self):
        correo = self.cleaned_data['correo_muni'].lower()
        if Usuario.objects.filter(correo_muni__iexact=correo).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Ya existe un funcionario con este correo.')
        return correo

    def clean_id_usuario(self):
        codigo = self.cleaned_data.get('id_usuario', '').strip().upper()
        if codigo and Usuario.objects.filter(id_usuario=codigo).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Ese ID ya está en uso.')
        return codigo

    def save(self, commit=True):
        obj = super().save(commit=False)
        if not obj.id_usuario:
            n = Usuario.objects.count() + 1
            while Usuario.objects.filter(id_usuario=f'USR-{n:03d}').exists():
                n += 1
            obj.id_usuario = f'USR-{n:03d}'
        if commit:
            obj.save()
        return obj


class _GrupoMixin(forms.Form):
    grupo = forms.ModelChoiceField(
        label='Perfil (grupo)', queryset=Group.objects.none(), empty_label='Seleccione un perfil')
    funcionario = forms.ModelChoiceField(
        label='Funcionario asociado', queryset=Usuario.objects.none(), required=False,
        empty_label='— Sin asociar —')

    def _preparar_grupos(self, actual=None):
        from .perfiles import PERFILES
        self.fields['grupo'].queryset = Group.objects.filter(name__in=PERFILES).order_by('name')
        libres = Usuario.objects.filter(user__isnull=True)
        if actual is not None and hasattr(actual, 'funcionario'):
            libres = Usuario.objects.filter(pk=actual.funcionario.pk) | libres
        self.fields['funcionario'].queryset = libres.order_by('nombre_completo')


class CuentaCrearForm(BootstrapMixin, _GrupoMixin, UserCreationForm):
    email = forms.EmailField(label='Correo electrónico', required=True,
                             help_text='Se usa para la recuperación de contraseña.')

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'is_active')
        labels = {'username': 'Nombre de usuario', 'first_name': 'Nombres',
                  'last_name': 'Apellidos', 'is_active': 'Cuenta activa'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._preparar_grupos()
        self.fields['is_active'].initial = True
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['password1'].label = 'Contraseña'
        self.fields['password2'].label = 'Confirmar contraseña'
        self._estilizar()

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Ya existe una cuenta con este correo.')
        return email

    def save(self, commit=True):
        user = super().save(commit=True)
        user.groups.set([self.cleaned_data['grupo']])
        func = self.cleaned_data.get('funcionario')
        if func:
            func.user = user
            func.save(update_fields=['user'])
        return user


class CuentaEditarForm(BootstrapMixin, _GrupoMixin, forms.ModelForm):
    password1 = forms.CharField(
        label='Nueva contraseña', required=False, strip=False, widget=forms.PasswordInput,
        help_text='Déjela en blanco para mantener la actual.')
    password2 = forms.CharField(
        label='Confirmar nueva contraseña', required=False, strip=False, widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'is_active')
        labels = {'username': 'Nombre de usuario', 'first_name': 'Nombres',
                  'last_name': 'Apellidos', 'email': 'Correo electrónico', 'is_active': 'Cuenta activa'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._preparar_grupos(self.instance)
        self.fields['email'].required = True
        grupo = self.instance.groups.first()
        if grupo:
            self.fields['grupo'].initial = grupo
        if hasattr(self.instance, 'funcionario'):
            self.fields['funcionario'].initial = self.instance.funcionario
        self._estilizar()

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Ya existe una cuenta con este correo.')
        return email

    def clean(self):
        datos = super().clean()
        p1, p2 = datos.get('password1'), datos.get('password2')
        if p1 or p2:
            if p1 != p2:
                self.add_error('password2', 'Las contraseñas no coinciden.')
            else:
                try:
                    password_validation.validate_password(p1, self.instance)
                except forms.ValidationError as e:
                    self.add_error('password1', e)
        return datos

    def save(self, commit=True):
        user = super().save(commit=True)
        if self.cleaned_data.get('password1'):
            user.set_password(self.cleaned_data['password1'])
            user.save(update_fields=['password'])
        user.groups.set([self.cleaned_data['grupo']])
        if hasattr(user, 'funcionario'):
            anterior = user.funcionario
            if anterior != self.cleaned_data.get('funcionario'):
                anterior.user = None
                anterior.save(update_fields=['user'])
        func = self.cleaned_data.get('funcionario')
        if func:
            func.user = user
            func.save(update_fields=['user'])
        return user
