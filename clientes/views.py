from django.db.models import Count, Q
from django.urls import reverse

from clientes.forms import ClienteForm, DireccionClienteForm
from clientes.models import Cliente, DireccionCliente
from comercios.access import accessible_commerces
from comercios.views import ManagedCreateView, ManagedDeleteView, ManagedListView, ManagedUpdateView


class ClienteListView(ManagedListView):
    model = Cliente
    template_name = "gestion/panel_clientes.html"
    commerce_lookup = "comercio"
    permission_required = "clientes.view_cliente"
    list_fields = ("id_cliente", "comercio", "nombre", "telefono", "correo")
    list_url_name = "clientes:cliente-list"
    create_url_name = "clientes:cliente-create"
    update_url_name = "clientes:cliente-update"
    delete_url_name = "clientes:cliente-delete"
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        self.scoped_queryset = queryset
        self.search_query = self.request.GET.get("q", "").strip()[:100]
        if self.search_query:
            queryset = queryset.filter(
                Q(nombre__icontains=self.search_query)
                | Q(telefono__icontains=self.search_query)
                | Q(correo__icontains=self.search_query)
            )
        return queryset.select_related("comercio").annotate(
            address_count=Count("direcciones")
        ).order_by("nombre", "pk")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        metrics = self.scoped_queryset.aggregate(
            total=Count("pk"),
            with_phone=Count(
                "pk", filter=Q(telefono__isnull=False) & ~Q(telefono="")
            ),
            with_email=Count(
                "pk", filter=Q(correo__isnull=False) & ~Q(correo="")
            ),
        )
        context.update(
            {
                "query": self.search_query,
                "total_clients": metrics["total"],
                "clients_with_phone": metrics["with_phone"],
                "clients_with_email": metrics["with_email"],
                "total_addresses": DireccionCliente.objects.filter(
                    cliente_id__in=self.scoped_queryset.order_by()
                ).count(),
                "has_commerces": accessible_commerces(self.request.user).exists(),
                "can_create_commerce": self.request.user.is_superuser,
                "account_label": self.request.user.get_username(),
                "can_change_client": self.request.user.has_perm(
                    "clientes.change_cliente"
                ),
                "can_delete_client": self.request.user.has_perm(
                    "clientes.delete_cliente"
                ),
                "home_url": reverse("cuentas:dashboard"),
            }
        )
        return context


class ClienteCreateView(ManagedCreateView):
    model = Cliente
    form_class = ClienteForm
    permission_required = "clientes.add_cliente"
    pass_user_to_form = True
    page_title = "Crear cliente"
    list_url_name = "clientes:cliente-list"


class ClienteUpdateView(ManagedUpdateView):
    model = Cliente
    form_class = ClienteForm
    commerce_lookup = "comercio"
    permission_required = "clientes.change_cliente"
    pass_user_to_form = True
    page_title = "Editar cliente"
    list_url_name = "clientes:cliente-list"


class ClienteDeleteView(ManagedDeleteView):
    model = Cliente
    commerce_lookup = "comercio"
    permission_required = "clientes.delete_cliente"
    page_title = "Eliminar cliente"
    list_url_name = "clientes:cliente-list"


class DireccionClienteListView(ManagedListView):
    model = DireccionCliente
    commerce_lookup = "cliente__comercio"
    permission_required = "clientes.view_direccioncliente"
    list_fields = ("id_direccion", "cliente", "alias", "ciudad", "predeterminada")
    list_url_name = "clientes:direccion-list"
    create_url_name = "clientes:direccion-create"
    update_url_name = "clientes:direccion-update"
    delete_url_name = "clientes:direccion-delete"


class DireccionClienteCreateView(ManagedCreateView):
    model = DireccionCliente
    form_class = DireccionClienteForm
    permission_required = "clientes.add_direccioncliente"
    pass_user_to_form = True
    page_title = "Crear dirección de cliente"
    list_url_name = "clientes:direccion-list"


class DireccionClienteUpdateView(ManagedUpdateView):
    model = DireccionCliente
    form_class = DireccionClienteForm
    commerce_lookup = "cliente__comercio"
    permission_required = "clientes.change_direccioncliente"
    pass_user_to_form = True
    page_title = "Editar dirección de cliente"
    list_url_name = "clientes:direccion-list"


class DireccionClienteDeleteView(ManagedDeleteView):
    model = DireccionCliente
    commerce_lookup = "cliente__comercio"
    permission_required = "clientes.delete_direccioncliente"
    page_title = "Eliminar dirección de cliente"
    list_url_name = "clientes:direccion-list"
