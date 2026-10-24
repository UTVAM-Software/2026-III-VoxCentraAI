from clientes.forms import ClienteForm, DireccionClienteForm
from clientes.models import Cliente, DireccionCliente
from comercios.views import ManagedCreateView, ManagedDeleteView, ManagedListView, ManagedUpdateView


class ClienteListView(ManagedListView):
    model = Cliente
    commerce_lookup = "comercio"
    permission_required = "clientes.view_cliente"
    list_fields = ("id_cliente", "comercio", "nombre", "telefono", "correo")
    list_url_name = "clientes:cliente-list"
    create_url_name = "clientes:cliente-create"
    update_url_name = "clientes:cliente-update"
    delete_url_name = "clientes:cliente-delete"


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
