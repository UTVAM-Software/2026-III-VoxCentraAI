from accesos.crud import ManagedListView, build_crud_views
from accesos.forms import InteraccionForm
from interacciones.models import Interaccion


class InteraccionListView(ManagedListView):
    model = Interaccion
    commerce_lookup = "comercio"
    branch_lookup = "sucursal"
    nullable_branch = True
    permission_required = "interacciones.view_interaccion"
    list_fields = (
        "id_interaccion",
        "comercio",
        "sucursal",
        "cliente",
        "canal",
        "estado",
        "iniciada_en",
    )
    list_url_name = "interacciones:interaccion-list"
    create_url_name = "interacciones:interaccion-create"
    update_url_name = "interacciones:interaccion-update"
    delete_url_name = "interacciones:interaccion-delete"


(
    interaccion_create_view,
    interaccion_update_view,
    interaccion_delete_view,
) = build_crud_views(
    Interaccion,
    InteraccionForm,
    "interacciones:interaccion-list",
    "interacción",
    commerce_lookup="comercio",
    branch_lookup="sucursal",
    nullable_branch=True,
)

from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render

from accesos.access import accessible_commerces, accessible_sucursales


@login_required
@permission_required("pedidos.add_pedido", raise_exception=True)
@permission_required("interacciones.add_interaccion", raise_exception=True)
def test_call(request):
    commerces = accessible_commerces(request.user).filter(estado="activo")
    branches = accessible_sucursales(request.user).filter(
        activa=True, comercio__in=commerces
    ).select_related("comercio")
    return render(request, "gestion/test_call.html", {
        "title": "Prueba de llamadas",
        "commerces": commerces,
        "branches": branches,
    })
