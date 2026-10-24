from django.http import Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse

from accesos.crud import ManagedDeleteView, ManagedListView, ManagedUpdateView, build_crud_views
from accesos.forms import AlcanceSucursalForm, MembresiaComercioForm, RolPlataformaForm
from accesos.models import AlcanceSucursal, MembresiaComercio, RolPlataforma


class RolListView(ManagedListView):
    model = RolPlataforma
    permission_required = "accesos.view_rolplataforma"
    superuser_only = True
    list_fields = ("usuario", "rol", "activo")
    list_url_name = "accesos:rol-list"
    create_url_name = "accesos:rol-create"
    update_url_name = "accesos:rol-update"
    delete_url_name = "accesos:rol-delete"


class MembresiaListView(ManagedListView):
    model = MembresiaComercio
    commerce_lookup = "comercio"
    permission_required = "accesos.view_membresiacomercio"
    superuser_only = True
    list_fields = ("usuario", "comercio", "rol", "activo")
    list_url_name = "accesos:membresia-list"
    create_url_name = "accesos:membresia-create"
    update_url_name = "accesos:membresia-update"
    delete_url_name = "accesos:membresia-delete"


class AlcanceListView(ManagedListView):
    model = AlcanceSucursal
    commerce_lookup = "membresia__comercio"
    permission_required = "accesos.view_alcancesucursal"
    superuser_only = True
    list_fields = ("membresia", "sucursal")
    list_url_name = "accesos:alcance-list"
    create_url_name = "accesos:alcance-create"
    update_url_name = "accesos:alcance-update"
    delete_url_name = "accesos:alcance-delete"

    def action_urls(self, obj):
        kwargs = {"membresia_id": obj.membresia_id, "sucursal_id": obj.sucursal_id}
        return {
            "edit_url": reverse(self.update_url_name, kwargs=kwargs),
            "delete_url": reverse(self.delete_url_name, kwargs=kwargs),
        }


class AlcanceObjectMixin:
    def get_object(self, queryset=None):
        queryset = queryset if queryset is not None else self.get_queryset()
        try:
            return get_object_or_404(
                queryset,
                membresia_id=self.kwargs["membresia_id"],
                sucursal_id=self.kwargs["sucursal_id"],
            )
        except (KeyError, ValueError, TypeError) as error:
            raise Http404 from error


class AlcanceUpdateView(AlcanceObjectMixin, ManagedUpdateView):
    model = AlcanceSucursal
    form_class = AlcanceSucursalForm
    permission_required = "accesos.change_alcancesucursal"
    superuser_only = True
    page_title = "Editar alcance de sucursal"
    list_url_name = "accesos:alcance-list"
    commerce_lookup = "membresia__comercio"


class AlcanceDeleteView(AlcanceObjectMixin, ManagedDeleteView):
    model = AlcanceSucursal
    permission_required = "accesos.delete_alcancesucursal"
    superuser_only = True
    page_title = "Eliminar alcance de sucursal"
    list_url_name = "accesos:alcance-list"
    commerce_lookup = "membresia__comercio"


(
    rol_create_view,
    rol_update_view,
    rol_delete_view,
) = build_crud_views(
    RolPlataforma,
    RolPlataformaForm,
    "accesos:rol-list",
    "rol de plataforma",
    superuser_only=True,
)
(
    membresia_create_view,
    membresia_update_view,
    membresia_delete_view,
) = build_crud_views(
    MembresiaComercio,
    MembresiaComercioForm,
    "accesos:membresia-list",
    "membresía de comercio",
    commerce_lookup="comercio",
    superuser_only=True,
)
alcance_create_view, _, _ = build_crud_views(
    AlcanceSucursal,
    AlcanceSucursalForm,
    "accesos:alcance-list",
    "alcance de sucursal",
    superuser_only=True,
)
alcance_update_view = AlcanceUpdateView.as_view()
alcance_delete_view = AlcanceDeleteView.as_view()
