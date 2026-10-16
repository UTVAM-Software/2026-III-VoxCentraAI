from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from .models import DetallePedido, HistorialPedido, OpcionDetalle, Pago, Pedido


@login_required
def resumen(request):
    return JsonResponse(
        {
            "pedidos": Pedido.objects.count(),
            "detalles": DetallePedido.objects.count(),
            "opciones": OpcionDetalle.objects.count(),
            "pagos": Pago.objects.count(),
            "eventos_historial": HistorialPedido.objects.count(),
        }
    )
