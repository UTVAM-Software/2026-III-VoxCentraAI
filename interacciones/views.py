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
