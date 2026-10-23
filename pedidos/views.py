from accesos.crud import ManagedListView, build_crud_views
from accesos.forms import (
    DetallePedidoForm,
    DireccionPedidoForm,
    HistorialPedidoForm,
    OpcionDetalleForm,
    PagoForm,
    PedidoForm,
)
from pedidos.models import (
    DetallePedido,
    DireccionPedido,
    HistorialPedido,
    OpcionDetalle,
    Pago,
    Pedido,
)


class PedidoListView(ManagedListView):
    model = Pedido
    commerce_lookup = "comercio"
    branch_lookup = "sucursal"
    permission_required = "pedidos.view_pedido"
    list_fields = (
        "id_pedido",
        "comercio",
        "sucursal",
        "cliente",
        "estado",
        "tipo_entrega",
        "total",
        "creado_en",
    )
    list_url_name = "pedidos:pedido-list"
    create_url_name = "pedidos:pedido-create"
    update_url_name = "pedidos:pedido-update"
    delete_url_name = "pedidos:pedido-delete"


class DireccionPedidoListView(ManagedListView):
    model = DireccionPedido
    commerce_lookup = "pedido__comercio"
    branch_lookup = "pedido__sucursal"
    permission_required = "pedidos.view_direccionpedido"
    list_fields = ("pedido", "calle", "colonia", "ciudad")
    list_url_name = "pedidos:direccion-list"
    create_url_name = "pedidos:direccion-create"
    update_url_name = "pedidos:direccion-update"
    delete_url_name = "pedidos:direccion-delete"


class DetallePedidoListView(ManagedListView):
    model = DetallePedido
    commerce_lookup = "pedido__comercio"
    branch_lookup = "pedido__sucursal"
    permission_required = "pedidos.view_detallepedido"
    list_fields = ("id_detalle", "pedido", "nombre_snapshot", "cantidad", "precio_unitario")
    list_url_name = "pedidos:detalle-list"
    create_url_name = "pedidos:detalle-create"
    update_url_name = "pedidos:detalle-update"
    delete_url_name = "pedidos:detalle-delete"


class OpcionDetalleListView(ManagedListView):
    model = OpcionDetalle
    commerce_lookup = "detalle__pedido__comercio"
    branch_lookup = "detalle__pedido__sucursal"
    permission_required = "pedidos.view_opciondetalle"
    list_fields = (
        "id_opcion_detalle",
        "detalle",
        "grupo_snapshot",
        "opcion_snapshot",
        "precio_adicional_snapshot",
    )
    list_url_name = "pedidos:opcion-detalle-list"
    create_url_name = "pedidos:opcion-detalle-create"
    update_url_name = "pedidos:opcion-detalle-update"
    delete_url_name = "pedidos:opcion-detalle-delete"


class PagoListView(ManagedListView):
    model = Pago
    commerce_lookup = "pedido__comercio"
    branch_lookup = "pedido__sucursal"
    permission_required = "pedidos.view_pago"
    list_fields = ("id_pago", "pedido", "metodo", "estado", "importe", "creado_en")
    list_url_name = "pedidos:pago-list"
    create_url_name = "pedidos:pago-create"
    update_url_name = "pedidos:pago-update"
    delete_url_name = "pedidos:pago-delete"


class HistorialPedidoListView(ManagedListView):
    model = HistorialPedido
    commerce_lookup = "pedido__comercio"
    branch_lookup = "pedido__sucursal"
    permission_required = "pedidos.view_historialpedido"
    superuser_only = True
    list_fields = (
        "id_evento",
        "pedido",
        "estado_anterior",
        "estado_nuevo",
        "cambiado_por",
        "creado_en",
    )
    list_url_name = "pedidos:historial-list"
    create_url_name = "pedidos:historial-create"
    update_url_name = "pedidos:historial-update"
    delete_url_name = "pedidos:historial-delete"


(
    pedido_create_view,
    pedido_update_view,
    pedido_delete_view,
) = build_crud_views(
    Pedido,
    PedidoForm,
    "pedidos:pedido-list",
    "pedido",
    commerce_lookup="comercio",
    branch_lookup="sucursal",
    set_user_field="creado_por",
)
(
    direccion_create_view,
    direccion_update_view,
    direccion_delete_view,
) = build_crud_views(
    DireccionPedido,
    DireccionPedidoForm,
    "pedidos:direccion-list",
    "dirección de pedido",
    commerce_lookup="pedido__comercio",
    branch_lookup="pedido__sucursal",
)
(
    detalle_create_view,
    detalle_update_view,
    detalle_delete_view,
) = build_crud_views(
    DetallePedido,
    DetallePedidoForm,
    "pedidos:detalle-list",
    "detalle de pedido",
    commerce_lookup="pedido__comercio",
    branch_lookup="pedido__sucursal",
)
(
    opcion_detalle_create_view,
    opcion_detalle_update_view,
    opcion_detalle_delete_view,
) = build_crud_views(
    OpcionDetalle,
    OpcionDetalleForm,
    "pedidos:opcion-detalle-list",
    "opción de detalle",
    commerce_lookup="detalle__pedido__comercio",
    branch_lookup="detalle__pedido__sucursal",
)
(
    pago_create_view,
    pago_update_view,
    pago_delete_view,
) = build_crud_views(
    Pago,
    PagoForm,
    "pedidos:pago-list",
    "pago",
    commerce_lookup="pedido__comercio",
    branch_lookup="pedido__sucursal",
)
(
    historial_create_view,
    historial_update_view,
    historial_delete_view,
) = build_crud_views(
    HistorialPedido,
    HistorialPedidoForm,
    "pedidos:historial-list",
    "evento del historial",
    commerce_lookup="pedido__comercio",
    branch_lookup="pedido__sucursal",
    superuser_only=True,
    set_user_field="cambiado_por",
)
