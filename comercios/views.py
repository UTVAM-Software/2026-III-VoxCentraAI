from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from .models import Comercio


def portada(request):
    return JsonResponse({"proyecto": "Voxcentra", "estado": "listo"})


@login_required
def resumen(request):
    return JsonResponse({"total_comercios": Comercio.objects.count()})
