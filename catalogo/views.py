from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from .models import Categoria, GrupoOpcion, OpcionProducto, Producto


@login_required
def resumen(request):
    return JsonResponse(
        {
            "categorias": Categoria.objects.count(),
            "productos": Producto.objects.count(),
            "grupos_opcion": GrupoOpcion.objects.count(),
            "opciones_producto": OpcionProducto.objects.count(),
        }
    )
