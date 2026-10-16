from django.contrib import admin

from .models import (
    DetallePedido,
    DireccionPedido,
    HistorialPedido,
    OpcionDetalle,
    Pago,
    Pedido,
)


admin.site.register(Pedido)
admin.site.register(DireccionPedido)
admin.site.register(DetallePedido)
admin.site.register(OpcionDetalle)
admin.site.register(Pago)
admin.site.register(HistorialPedido)
