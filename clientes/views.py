from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from .models import Cliente, DireccionCliente


@login_required
def resumen(request):
    return JsonResponse(
        {"clientes": Cliente.objects.count(), "direcciones": DireccionCliente.objects.count()}
    )
