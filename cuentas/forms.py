from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, SetPasswordForm, UserCreationForm
from django.contrib.auth.models import Group, Permission


User = get_user_model()


class VoxcentraAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Nombre de usuario'
        self.fields['password'].label = 'Contraseña'


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
