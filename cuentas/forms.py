from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, SetPasswordForm, UserCreationForm
from django.core.validators import MaxLengthValidator
from django.contrib.auth.models import Group, Permission


User = get_user_model()

MAX_PASSWORD_LENGTH = 128


def configure_password_length(field):
    """Enforce a generous password maximum in both Django and the browser."""
    field.max_length = MAX_PASSWORD_LENGTH
    if not any(
        isinstance(validator, MaxLengthValidator)
        and validator.limit_value == MAX_PASSWORD_LENGTH
        for validator in field.validators
    ):
        field.validators.append(MaxLengthValidator(MAX_PASSWORD_LENGTH))
    field.widget.attrs.update({
        'maxlength': str(MAX_PASSWORD_LENGTH),
        'minlength': '15',
    })


class VoxcentraAuthenticationForm(AuthenticationForm):
    password = forms.CharField(
        label='Contraseña',
        strip=False,
        min_length=15,
        max_length=MAX_PASSWORD_LENGTH,
        widget=forms.PasswordInput(attrs={
            'autocomplete': 'current-password',
            'maxlength': str(MAX_PASSWORD_LENGTH),
            'minlength': '15',
            'aria-describedby': 'password-hint',
        }),
    )
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Nombre de usuario'
        self.fields['username'].widget.attrs.update({
            'autocomplete': 'username',
            'autocapitalize': 'none',
            'spellcheck': 'false',
        })
        self.fields['password'].label = 'Contraseña'
        self.fields['password'].widget.attrs['autocomplete'] = 'current-password'


class AuthUserCreationForm(UserCreationForm):
    """Crea usuarios regulares y permite asignarles grupos y permisos."""

    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'is_active',
            'groups',
            'user_permissions',
        )
        widgets = {
            'groups': forms.SelectMultiple(attrs={'class': 'field-select-multiple'}),
            'user_permissions': forms.SelectMultiple(attrs={'class': 'field-select-multiple'}),
        }
        labels = {
            'username': 'Nombre de usuario',
            'email': 'Correo electrónico',
            'first_name': 'Nombre',
            'last_name': 'Apellidos',
            'is_active': 'Cuenta activa',
            'groups': 'Grupos',
            'user_permissions': 'Permisos directos',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].label = 'Contraseña'
        self.fields['password2'].label = 'Confirmar contraseña'
        configure_password_length(self.fields['password1'])
        configure_password_length(self.fields['password2'])


class AuthUserChangeForm(forms.ModelForm):
    """Edita datos y permisos sin exponer contraseñas ni privilegios de superusuario."""

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'is_active',
            'groups',
            'user_permissions',
        )
        widgets = {
            'groups': forms.SelectMultiple(attrs={'class': 'field-select-multiple'}),
            'user_permissions': forms.SelectMultiple(attrs={'class': 'field-select-multiple'}),
        }
        labels = {
            'username': 'Nombre de usuario',
            'email': 'Correo electrónico',
            'first_name': 'Nombre',
            'last_name': 'Apellidos',
            'is_active': 'Cuenta activa',
            'groups': 'Grupos',
            'user_permissions': 'Permisos directos',
        }


class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ('name', 'permissions')
        labels = {
            'name': 'Nombre del grupo',
            'permissions': 'Permisos asignados',
        }
        widgets = {
            'permissions': forms.SelectMultiple(attrs={'class': 'field-select-multiple'}),
        }


class PermissionForm(forms.ModelForm):
    class Meta:
        model = Permission
        fields = ('name', 'content_type', 'codename')
        labels = {
            'name': 'Nombre',
            'content_type': 'Tipo de contenido',
            'codename': 'Código del permiso',
        }


class AuthUserPasswordForm(SetPasswordForm):
    """Cambia la contraseña con validación de Django sin guardar texto plano."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['new_password1'].label = 'Nueva contraseña'
        self.fields['new_password2'].label = 'Confirmar nueva contraseña'
        configure_password_length(self.fields['new_password1'])
        configure_password_length(self.fields['new_password2'])
