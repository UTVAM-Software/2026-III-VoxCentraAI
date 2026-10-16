from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from .models import MembresiaComercio, RolPlataforma


@login_required
def resumen(request):
    return JsonResponse(
        {
            "roles_plataforma": RolPlataforma.objects.count(),
            "membresias": MembresiaComercio.objects.count(),
        }
    )
