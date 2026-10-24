from django import forms

from clientes.models import Cliente, DireccionCliente
from comercios.access import accessible_commerces, queryset_for_user


class ClienteForm(forms.ModelForm):
    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        self.fields["comercio"].queryset = accessible_commerces(user)

    class Meta:
        model = Cliente
        fields = ("comercio", "nombre", "telefono", "correo")


class DireccionClienteForm(forms.ModelForm):
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["cliente"].queryset = queryset_for_user(
            Cliente.objects.all(), user, "comercio"
        )

    class Meta:
        model = DireccionCliente
        fields = (
            "cliente",
            "alias",
            "calle",
            "numero_exterior",
            "numero_interior",
            "colonia",
            "ciudad",
            "codigo_postal",
            "referencias",
            "predeterminada",
        )
