from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from comercios.access import accessible_sucursales, queryset_for_user
from comercios.forms import (
    ComercioForm,
    ConfiguracionComercioCreateForm,
    ConfiguracionComercioUpdateForm,
    SucursalForm,
)
from comercios.models import Comercio, ConfiguracionComercio, Sucursal


class PermissionRequiredLoginMixin(LoginRequiredMixin, PermissionRequiredMixin):
    """Require an authenticated user and the model permission for every action."""

    raise_exception = True


class CommerceQuerysetScopeMixin:
    commerce_lookup = None
    branch_lookup = None
    branch_scope = False

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.branch_scope:
            queryset = queryset.filter(pk__in=accessible_sucursales(self.request.user))
        if self.branch_lookup:
            queryset = queryset.filter(
                **{
                    f"{self.branch_lookup}__in": accessible_sucursales(
                        self.request.user
                    ).values("pk")
                }
            )
        if self.commerce_lookup:
            queryset = queryset_for_user(
                queryset, self.request.user, self.commerce_lookup
            )
        if self.branch_scope or self.branch_lookup or self.commerce_lookup:
            return queryset
        return queryset.none()


class SuperuserMutationMixin:
    """Keep creation or removal of top-level commerce records to superusers."""

    def has_permission(self):
        return self.request.user.is_superuser and super().has_permission()


class ManagedListView(PermissionRequiredLoginMixin, CommerceQuerysetScopeMixin, ListView):
    template_name = "gestion/object_list.html"
    list_fields = ()
    list_url_name = ""
    create_url_name = ""
    update_url_name = ""
    delete_url_name = ""
    create_superuser_only = False
    delete_superuser_only = False

    def action_urls(self, obj):
        kwargs = {"pk": obj.pk}
        return {
            "edit_url": reverse(self.update_url_name, kwargs=kwargs),
            "delete_url": reverse(self.delete_url_name, kwargs=kwargs),
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model = self.model
        context["title"] = model._meta.verbose_name_plural.capitalize()
        context["list_url"] = reverse(self.list_url_name)
        add_permission = f"{model._meta.app_label}.add_{model._meta.model_name}"
        change_permission = f"{model._meta.app_label}.change_{model._meta.model_name}"
        delete_permission = f"{model._meta.app_label}.delete_{model._meta.model_name}"
        context["create_url"] = reverse(self.create_url_name)
        context["can_create"] = self.request.user.has_perm(add_permission) and (
            not self.create_superuser_only or self.request.user.is_superuser
        )
        context["columns"] = [
            model._meta.get_field(field_name).verbose_name.capitalize()
            for field_name in self.list_fields
        ]
        context["rows"] = []
        for obj in context["object_list"]:
            urls = self.action_urls(obj)
            context["rows"].append(
                {
                    "values": [getattr(obj, field_name) for field_name in self.list_fields],
                    "edit_url": (
                        urls["edit_url"]
                        if self.request.user.has_perm(change_permission)
                        else None
                    ),
                    "delete_url": (
                        urls["delete_url"]
                        if self.request.user.has_perm(delete_permission)
                        and (not self.delete_superuser_only or self.request.user.is_superuser)
                        else None
                    ),
                }
            )
        return context


class ManagedCreateView(PermissionRequiredLoginMixin, CreateView):
    template_name = "gestion/object_form.html"
    list_url_name = ""
    page_title = ""
    pass_user_to_form = False

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.pass_user_to_form:
            kwargs["user"] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = self.page_title
        context["list_url"] = reverse(self.list_url_name)
        return context

    def get_success_url(self):
        return reverse(self.list_url_name)


class ManagedUpdateView(PermissionRequiredLoginMixin, CommerceQuerysetScopeMixin, UpdateView):
    template_name = "gestion/object_form.html"
    list_url_name = ""
    page_title = ""
    pass_user_to_form = False

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.pass_user_to_form:
            kwargs["user"] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = self.page_title
        context["list_url"] = reverse(self.list_url_name)
        return context

    def get_success_url(self):
        return reverse(self.list_url_name)


class ManagedDeleteView(PermissionRequiredLoginMixin, CommerceQuerysetScopeMixin, DeleteView):
    template_name = "gestion/object_confirm_delete.html"
    list_url_name = ""
    page_title = ""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = self.page_title
        context["list_url"] = reverse(self.list_url_name)
        return context

    def get_success_url(self):
        return reverse(self.list_url_name)


class ComercioListView(ManagedListView):
    model = Comercio
    commerce_lookup = "pk"
    permission_required = "comercios.view_comercio"
    list_fields = ("id_comercio", "nombre_comercial", "giro", "estado")
    list_url_name = "comercios:comercio-list"
    create_url_name = "comercios:comercio-create"
    update_url_name = "comercios:comercio-update"
    delete_url_name = "comercios:comercio-delete"
    create_superuser_only = True
    delete_superuser_only = True


class ComercioCreateView(SuperuserMutationMixin, ManagedCreateView):
    model = Comercio
    form_class = ComercioForm
    permission_required = "comercios.add_comercio"
    page_title = "Crear comercio"
    list_url_name = "comercios:comercio-list"


class ComercioUpdateView(ManagedUpdateView):
    model = Comercio
    form_class = ComercioForm
    commerce_lookup = "pk"
    permission_required = "comercios.change_comercio"
    page_title = "Editar comercio"
    list_url_name = "comercios:comercio-list"


class ComercioDeleteView(SuperuserMutationMixin, ManagedDeleteView):
    model = Comercio
    commerce_lookup = "pk"
    permission_required = "comercios.delete_comercio"
    page_title = "Eliminar comercio"
    list_url_name = "comercios:comercio-list"


class SucursalListView(ManagedListView):
    model = Sucursal
    branch_scope = True
    permission_required = "comercios.view_sucursal"
    list_fields = ("id_sucursal", "comercio", "nombre", "activa")
    list_url_name = "comercios:sucursal-list"
    create_url_name = "comercios:sucursal-create"
    update_url_name = "comercios:sucursal-update"
    delete_url_name = "comercios:sucursal-delete"


class SucursalCreateView(ManagedCreateView):
    model = Sucursal
    form_class = SucursalForm
    permission_required = "comercios.add_sucursal"
    pass_user_to_form = True
    page_title = "Crear sucursal"
    list_url_name = "comercios:sucursal-list"


class SucursalUpdateView(ManagedUpdateView):
    model = Sucursal
    form_class = SucursalForm
    branch_scope = True
    permission_required = "comercios.change_sucursal"
    pass_user_to_form = True
    page_title = "Editar sucursal"
    list_url_name = "comercios:sucursal-list"


class SucursalDeleteView(ManagedDeleteView):
    model = Sucursal
    branch_scope = True
    permission_required = "comercios.delete_sucursal"
    page_title = "Eliminar sucursal"
    list_url_name = "comercios:sucursal-list"


class ConfiguracionListView(ManagedListView):
    model = ConfiguracionComercio
    commerce_lookup = "comercio"
    permission_required = "comercios.view_configuracioncomercio"
    list_fields = ("comercio", "canal_voz_activo", "actualizado_en")
    list_url_name = "comercios:configuracion-list"
    create_url_name = "comercios:configuracion-create"
    update_url_name = "comercios:configuracion-update"
    delete_url_name = "comercios:configuracion-delete"


class ConfiguracionCreateView(ManagedCreateView):
    model = ConfiguracionComercio
    form_class = ConfiguracionComercioCreateForm
    permission_required = "comercios.add_configuracioncomercio"
    pass_user_to_form = True
    page_title = "Crear configuración de comercio"
    list_url_name = "comercios:configuracion-list"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs


class ConfiguracionUpdateView(ManagedUpdateView):
    model = ConfiguracionComercio
    form_class = ConfiguracionComercioUpdateForm
    commerce_lookup = "comercio"
    permission_required = "comercios.change_configuracioncomercio"
    page_title = "Editar configuración de comercio"
    list_url_name = "comercios:configuracion-list"


class ConfiguracionDeleteView(ManagedDeleteView):
    model = ConfiguracionComercio
    commerce_lookup = "comercio"
    permission_required = "comercios.delete_configuracioncomercio"
    page_title = "Eliminar configuración de comercio"
    list_url_name = "comercios:configuracion-list"
