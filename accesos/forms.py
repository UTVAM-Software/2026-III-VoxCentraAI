from django import forms

from accesos.access import accessible_commerces, accessible_sucursales, queryset_for_user
from accesos.models import AlcanceSucursal, MembresiaComercio, RolPlataforma
from catalogo.models import OpcionProducto, Producto
from clientes.models import Cliente
from interacciones.models import Interaccion
from pedidos.models import (
    DetallePedido,
    DireccionPedido,
    HistorialPedido,
    OpcionDetalle,
    Pago,
    Pedido,
)


class ScopedModelForm(forms.ModelForm):
    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)


class RolPlataformaForm(ScopedModelForm):
    class Meta:
        model = RolPlataforma
        fields = ("usuario", "rol", "activo")


class MembresiaComercioForm(ScopedModelForm):
    class Meta:
        model = MembresiaComercio
        fields = ("usuario", "comercio", "rol", "activo")


class AlcanceSucursalForm(ScopedModelForm):
    class Meta:
        model = AlcanceSucursal
        fields = ("membresia", "sucursal")


class InteraccionForm(ScopedModelForm):
    class Meta:
        model = Interaccion
        fields = (
            "comercio",
            "sucursal",
            "cliente",
            "canal",
            "estado",
            "terminada_en",
            "referencia_externa",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["comercio"].queryset = accessible_commerces(self.user)
        self.fields["sucursal"].queryset = accessible_sucursales(self.user)
        self.fields["cliente"].queryset = queryset_for_user(
            Cliente.objects.all(), self.user, "comercio"
        )


class PedidoForm(ScopedModelForm):
    class Meta:
        model = Pedido
        fields = (
            "comercio",
            "sucursal",
            "cliente",
            "interaccion",
            "origen",
            "estado",
            "tipo_entrega",
            "moneda",
            "subtotal",
            "descuento",
            "impuestos",
            "total",
            "notas",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["comercio"].queryset = accessible_commerces(self.user)
        self.fields["sucursal"].queryset = accessible_sucursales(self.user)
        self.fields["cliente"].queryset = queryset_for_user(
            Cliente.objects.all(), self.user, "comercio"
        )
        self.fields["interaccion"].queryset = queryset_for_user(
            Interaccion.objects.all(), self.user, "comercio"
        )


class DireccionPedidoForm(ScopedModelForm):
    class Meta:
        model = DireccionPedido
        fields = (
            "pedido",
            "calle",
            "numero_exterior",
            "numero_interior",
            "colonia",
            "ciudad",
            "codigo_postal",
            "referencias",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["pedido"].queryset = queryset_for_user(
            Pedido.objects.all(), self.user, "comercio"
        )


class DetallePedidoForm(ScopedModelForm):
    class Meta:
        model = DetallePedido
        fields = (
            "pedido",
            "producto",
            "sku_snapshot",
            "nombre_snapshot",
            "cantidad",
            "precio_unitario",
            "notas",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["pedido"].queryset = queryset_for_user(
            Pedido.objects.all(), self.user, "comercio"
        )
        self.fields["producto"].queryset = queryset_for_user(
            Producto.objects.all(), self.user, "comercio"
        )


class OpcionDetalleForm(ScopedModelForm):
    class Meta:
        model = OpcionDetalle
        fields = (
            "detalle",
            "opcion_producto",
            "grupo_snapshot",
            "opcion_snapshot",
            "precio_adicional_snapshot",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["detalle"].queryset = queryset_for_user(
            DetallePedido.objects.all(), self.user, "pedido__comercio"
        )
        self.fields["opcion_producto"].queryset = queryset_for_user(
            OpcionProducto.objects.all(), self.user, "grupo__producto__comercio"
        )


class PagoForm(ScopedModelForm):
    class Meta:
        model = Pago
        fields = ("pedido", "metodo", "estado", "importe", "referencia_externa", "pagado_en")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["pedido"].queryset = queryset_for_user(
            Pedido.objects.all(), self.user, "comercio"
        )


class HistorialPedidoForm(ScopedModelForm):
    class Meta:
        model = HistorialPedido
        fields = ("pedido", "estado_anterior", "estado_nuevo", "nota")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["pedido"].queryset = queryset_for_user(
            Pedido.objects.all(), self.user, "comercio"
        )
