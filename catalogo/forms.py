from django import forms
from django.core.exceptions import ValidationError

from catalogo.models import (
    Categoria,
    GrupoOpcion,
    OpcionProducto,
    Producto,
    SucursalProducto,
)
from comercios.access import accessible_commerces, accessible_sucursales, queryset_for_user
from comercios.models import Sucursal


class ScopedModelForm(forms.ModelForm):
    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def commerce_queryset(self):
        return accessible_commerces(self.user)


class CategoriaForm(ScopedModelForm):
    class Meta:
        model = Categoria
        fields = ("comercio", "categoria_padre", "nombre", "orden", "activa")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        commerces = self.commerce_queryset()
        self.fields["comercio"].queryset = commerces
        categories = queryset_for_user(Categoria.objects.all(), self.user, "comercio")
        commerce_id = self.data.get("comercio") or getattr(self.instance, "comercio_id", None)
        if commerce_id:
            categories = categories.filter(comercio_id=commerce_id)
        self.fields["categoria_padre"].queryset = categories

    def clean(self):
        cleaned_data = super().clean()
        commerce = cleaned_data.get("comercio")
        parent = cleaned_data.get("categoria_padre")
        if commerce and parent and parent.comercio_id != commerce.pk:
            self.add_error("categoria_padre", "La categoría padre debe pertenecer al mismo comercio.")
        return cleaned_data


class ProductoForm(ScopedModelForm):
    class Meta:
        model = Producto
        fields = (
            "comercio",
            "categoria",
            "sku",
            "nombre",
            "descripcion",
            "precio_base",
            "activo",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["comercio"].queryset = self.commerce_queryset()
        categories = queryset_for_user(Categoria.objects.all(), self.user, "comercio")
        commerce_id = self.data.get("comercio") or getattr(self.instance, "comercio_id", None)
        if commerce_id:
            categories = categories.filter(comercio_id=commerce_id)
        self.fields["categoria"].queryset = categories


class GrupoOpcionForm(ScopedModelForm):
    class Meta:
        model = GrupoOpcion
        fields = ("producto", "nombre", "min_selecciones", "max_selecciones", "orden")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["producto"].queryset = queryset_for_user(
            Producto.objects.all(), self.user, "comercio"
        )


class OpcionProductoForm(ScopedModelForm):
    class Meta:
        model = OpcionProducto
        fields = ("grupo", "nombre", "precio_adicional", "activa", "orden")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["grupo"].queryset = queryset_for_user(
            GrupoOpcion.objects.all(), self.user, "producto__comercio"
        )


class SucursalProductoForm(forms.Form):
    sucursal = forms.ModelChoiceField(queryset=Sucursal.objects.none())
    producto = forms.ModelChoiceField(queryset=Producto.objects.none())
    precio_override = forms.DecimalField(max_digits=12, decimal_places=2, required=False)
    disponible = forms.BooleanField(required=False, initial=True)

    def __init__(self, *args, user=None, instance=None, **kwargs):
        self.user = user
        self.instance = instance
        super().__init__(*args, **kwargs)
        self.fields["sucursal"].queryset = accessible_sucursales(user)
        self.fields["producto"].queryset = queryset_for_user(
            Producto.objects.all(), user, "comercio"
        )
        if instance is not None and not self.is_bound:
            self.initial.update(
                {
                    "sucursal": instance.sucursal_id,
                    "producto": instance.producto_id,
                    "precio_override": instance.precio_override,
                    "disponible": instance.disponible,
                }
            )

    def clean(self):
        cleaned_data = super().clean()
        branch = cleaned_data.get("sucursal")
        product = cleaned_data.get("producto")
        if branch and product and branch.comercio_id != product.comercio_id:
            raise ValidationError("La sucursal y el producto deben pertenecer al mismo comercio.")
        return cleaned_data

    def save(self):
        obj = self.instance or SucursalProducto()
        obj.sucursal = self.cleaned_data["sucursal"]
        obj.producto = self.cleaned_data["producto"]
        obj.precio_override = self.cleaned_data["precio_override"]
        obj.disponible = self.cleaned_data["disponible"]
        obj.save()
        return obj
