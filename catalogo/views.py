from django.http import Http404
from django.urls import reverse

from catalogo.forms import (
    CategoriaForm,
    GrupoOpcionForm,
    OpcionProductoForm,
    ProductoForm,
    SucursalProductoForm,
)
from catalogo.models import (
    Categoria,
    GrupoOpcion,
    OpcionProducto,
    Producto,
    SucursalProducto,
)
from comercios.views import (
    ManagedCreateView,
    ManagedDeleteView,
    ManagedListView,
    ManagedUpdateView,
)


class CategoriaListView(ManagedListView):
    model = Categoria
    commerce_lookup = "comercio"
    permission_required = "catalogo.view_categoria"
    list_fields = ("id_categoria", "comercio", "categoria_padre", "nombre", "activa")
    list_url_name = "catalogo:categoria-list"
    create_url_name = "catalogo:categoria-create"
    update_url_name = "catalogo:categoria-update"
    delete_url_name = "catalogo:categoria-delete"


class CategoriaCreateView(ManagedCreateView):
    model = Categoria
    form_class = CategoriaForm
    permission_required = "catalogo.add_categoria"
    pass_user_to_form = True
    page_title = "Crear categoría"
    list_url_name = "catalogo:categoria-list"


class CategoriaUpdateView(ManagedUpdateView):
    model = Categoria
    form_class = CategoriaForm
    commerce_lookup = "comercio"
    permission_required = "catalogo.change_categoria"
    pass_user_to_form = True
    page_title = "Editar categoría"
    list_url_name = "catalogo:categoria-list"


class CategoriaDeleteView(ManagedDeleteView):
    model = Categoria
    commerce_lookup = "comercio"
    permission_required = "catalogo.delete_categoria"
    page_title = "Eliminar categoría"
    list_url_name = "catalogo:categoria-list"


class ProductoListView(ManagedListView):
    model = Producto
    commerce_lookup = "comercio"
    permission_required = "catalogo.view_producto"
    list_fields = ("id_producto", "comercio", "categoria", "nombre", "precio_base", "activo")
    list_url_name = "catalogo:producto-list"
    create_url_name = "catalogo:producto-create"
    update_url_name = "catalogo:producto-update"
    delete_url_name = "catalogo:producto-delete"


class ProductoCreateView(ManagedCreateView):
    model = Producto
    form_class = ProductoForm
    permission_required = "catalogo.add_producto"
    pass_user_to_form = True
    page_title = "Crear producto"
    list_url_name = "catalogo:producto-list"


class ProductoUpdateView(ManagedUpdateView):
    model = Producto
    form_class = ProductoForm
    commerce_lookup = "comercio"
    permission_required = "catalogo.change_producto"
    pass_user_to_form = True
    page_title = "Editar producto"
    list_url_name = "catalogo:producto-list"


class ProductoDeleteView(ManagedDeleteView):
    model = Producto
    commerce_lookup = "comercio"
    permission_required = "catalogo.delete_producto"
    page_title = "Eliminar producto"
    list_url_name = "catalogo:producto-list"


class SucursalProductoListView(ManagedListView):
    model = SucursalProducto
    branch_lookup = "sucursal_id"
    commerce_lookup = "producto__comercio"
    permission_required = "catalogo.view_sucursalproducto"
    list_fields = ("sucursal", "producto", "precio_override", "disponible")
    list_url_name = "catalogo:sucursal-producto-list"
    create_url_name = "catalogo:sucursal-producto-create"
    update_url_name = "catalogo:sucursal-producto-update"
    delete_url_name = "catalogo:sucursal-producto-delete"

    def action_urls(self, obj):
        kwargs = {"sucursal_id": obj.sucursal_id, "producto_id": obj.producto_id}
        return {
            "edit_url": reverse(self.update_url_name, kwargs=kwargs),
            "delete_url": reverse(self.delete_url_name, kwargs=kwargs),
        }


class SucursalProductoCreateView(ManagedCreateView):
    model = SucursalProducto
    form_class = SucursalProductoForm
    permission_required = "catalogo.add_sucursalproducto"
    pass_user_to_form = True
    page_title = "Asignar producto a sucursal"
    list_url_name = "catalogo:sucursal-producto-list"


class SucursalProductoUpdateView(ManagedUpdateView):
    model = SucursalProducto
    form_class = SucursalProductoForm
    branch_lookup = "sucursal_id"
    commerce_lookup = "producto__comercio"
    permission_required = "catalogo.change_sucursalproducto"
    pass_user_to_form = True
    page_title = "Editar producto en sucursal"
    list_url_name = "catalogo:sucursal-producto-list"

    def get_object(self, queryset=None):
        queryset = queryset if queryset is not None else self.get_queryset()
        try:
            return queryset.get(
                sucursal_id=self.kwargs["sucursal_id"],
                producto_id=self.kwargs["producto_id"],
            )
        except SucursalProducto.DoesNotExist as error:
            raise Http404 from error


class SucursalProductoDeleteView(ManagedDeleteView):
    model = SucursalProducto
    branch_lookup = "sucursal_id"
    commerce_lookup = "producto__comercio"
    permission_required = "catalogo.delete_sucursalproducto"
    page_title = "Eliminar producto de sucursal"
    list_url_name = "catalogo:sucursal-producto-list"

    def get_object(self, queryset=None):
        queryset = queryset if queryset is not None else self.get_queryset()
        try:
            return queryset.get(
                sucursal_id=self.kwargs["sucursal_id"],
                producto_id=self.kwargs["producto_id"],
            )
        except SucursalProducto.DoesNotExist as error:
            raise Http404 from error


class GrupoOpcionListView(ManagedListView):
    model = GrupoOpcion
    commerce_lookup = "producto__comercio"
    permission_required = "catalogo.view_grupoopcion"
    list_fields = ("id_grupo", "producto", "nombre", "min_selecciones", "max_selecciones")
    list_url_name = "catalogo:grupo-opcion-list"
    create_url_name = "catalogo:grupo-opcion-create"
    update_url_name = "catalogo:grupo-opcion-update"
    delete_url_name = "catalogo:grupo-opcion-delete"


class GrupoOpcionCreateView(ManagedCreateView):
    model = GrupoOpcion
    form_class = GrupoOpcionForm
    permission_required = "catalogo.add_grupoopcion"
    pass_user_to_form = True
    page_title = "Crear grupo de opciones"
    list_url_name = "catalogo:grupo-opcion-list"


class GrupoOpcionUpdateView(ManagedUpdateView):
    model = GrupoOpcion
    form_class = GrupoOpcionForm
    commerce_lookup = "producto__comercio"
    permission_required = "catalogo.change_grupoopcion"
    pass_user_to_form = True
    page_title = "Editar grupo de opciones"
    list_url_name = "catalogo:grupo-opcion-list"


class GrupoOpcionDeleteView(ManagedDeleteView):
    model = GrupoOpcion
    commerce_lookup = "producto__comercio"
    permission_required = "catalogo.delete_grupoopcion"
    page_title = "Eliminar grupo de opciones"
    list_url_name = "catalogo:grupo-opcion-list"


class OpcionProductoListView(ManagedListView):
    model = OpcionProducto
    commerce_lookup = "grupo__producto__comercio"
    permission_required = "catalogo.view_opcionproducto"
    list_fields = ("id_opcion", "grupo", "nombre", "precio_adicional", "activa")
    list_url_name = "catalogo:opcion-producto-list"
    create_url_name = "catalogo:opcion-producto-create"
    update_url_name = "catalogo:opcion-producto-update"
    delete_url_name = "catalogo:opcion-producto-delete"


class OpcionProductoCreateView(ManagedCreateView):
    model = OpcionProducto
    form_class = OpcionProductoForm
    permission_required = "catalogo.add_opcionproducto"
    pass_user_to_form = True
    page_title = "Crear opción de producto"
    list_url_name = "catalogo:opcion-producto-list"


class OpcionProductoUpdateView(ManagedUpdateView):
    model = OpcionProducto
    form_class = OpcionProductoForm
    commerce_lookup = "grupo__producto__comercio"
    permission_required = "catalogo.change_opcionproducto"
    pass_user_to_form = True
    page_title = "Editar opción de producto"
    list_url_name = "catalogo:opcion-producto-list"


class OpcionProductoDeleteView(ManagedDeleteView):
    model = OpcionProducto
    commerce_lookup = "grupo__producto__comercio"
    permission_required = "catalogo.delete_opcionproducto"
    page_title = "Eliminar opción de producto"
    list_url_name = "catalogo:opcion-producto-list"
