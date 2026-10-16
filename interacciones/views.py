from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from .models import Interaccion


@login_required
def resumen(request):
    return JsonResponse({"interacciones": Interaccion.objects.count()})
