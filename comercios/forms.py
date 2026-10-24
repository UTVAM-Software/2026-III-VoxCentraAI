from django import forms

from comercios.access import (
    accessible_commerces,
    commerces_with_unrestricted_branch_access,
)
from comercios.models import Comercio, ConfiguracionComercio, Sucursal


class UserScopedModelForm(forms.ModelForm):
    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def commerce_queryset(self):
        return accessible_commerces(self.user)


class ComercioForm(forms.ModelForm):
    class Meta:
        model = Comercio
        fields = ("nombre_comercial", "slug", "giro", "moneda", "zona_horaria", "estado")


class SucursalForm(UserScopedModelForm):
    class Meta:
        model = Sucursal
        fields = ("comercio", "nombre", "direccion", "activa")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        commerces = self.commerce_queryset()
        if self.instance.pk:
            self.fields["comercio"].disabled = True
        elif self.user and not self.user.is_superuser:
            # A user with branch-level restrictions can manage assigned branches,
            # but cannot create a new branch under a restricted membership.
            commerces = commerces_with_unrestricted_branch_access(self.user)
        self.fields["comercio"].queryset = commerces


class ConfiguracionComercioCreateForm(UserScopedModelForm):
    class Meta:
        model = ConfiguracionComercio
        fields = ("comercio", "saludo", "instrucciones_atencion", "canal_voz_activo")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["comercio"].queryset = self.commerce_queryset().filter(
            configuracion__isnull=True
        )


class ConfiguracionComercioUpdateForm(forms.ModelForm):
    class Meta:
        model = ConfiguracionComercio
        fields = ("saludo", "instrucciones_atencion", "canal_voz_activo")
