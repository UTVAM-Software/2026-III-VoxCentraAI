from django.urls import path

from catalogo import views

app_name = "catalogo"

urlpatterns = [
    path("categorias/", views.CategoriaListView.as_view(), name="categoria-list"),
    path("categorias/nueva/", views.CategoriaCreateView.as_view(), name="categoria-create"),
    path("categorias/<int:pk>/editar/", views.CategoriaUpdateView.as_view(), name="categoria-update"),
    path("categorias/<int:pk>/eliminar/", views.CategoriaDeleteView.as_view(), name="categoria-delete"),
    path("productos/", views.ProductoListView.as_view(), name="producto-list"),
    path("productos/nuevo/", views.ProductoCreateView.as_view(), name="producto-create"),
    path("productos/<int:pk>/editar/", views.ProductoUpdateView.as_view(), name="producto-update"),
    path("productos/<int:pk>/eliminar/", views.ProductoDeleteView.as_view(), name="producto-delete"),
    path("sucursales-productos/", views.SucursalProductoListView.as_view(), name="sucursal-producto-list"),
    path("sucursales-productos/nuevo/", views.SucursalProductoCreateView.as_view(), name="sucursal-producto-create"),
    path(
        "sucursales-productos/<int:sucursal_id>/<int:producto_id>/editar/",
        views.SucursalProductoUpdateView.as_view(),
        name="sucursal-producto-update",
    ),
    path(
        "sucursales-productos/<int:sucursal_id>/<int:producto_id>/eliminar/",
        views.SucursalProductoDeleteView.as_view(),
        name="sucursal-producto-delete",
    ),
    path("grupos-opcion/", views.GrupoOpcionListView.as_view(), name="grupo-opcion-list"),
    path("grupos-opcion/nuevo/", views.GrupoOpcionCreateView.as_view(), name="grupo-opcion-create"),
    path("grupos-opcion/<int:pk>/editar/", views.GrupoOpcionUpdateView.as_view(), name="grupo-opcion-update"),
    path("grupos-opcion/<int:pk>/eliminar/", views.GrupoOpcionDeleteView.as_view(), name="grupo-opcion-delete"),
    path("opciones-producto/", views.OpcionProductoListView.as_view(), name="opcion-producto-list"),
    path("opciones-producto/nueva/", views.OpcionProductoCreateView.as_view(), name="opcion-producto-create"),
    path("opciones-producto/<int:pk>/editar/", views.OpcionProductoUpdateView.as_view(), name="opcion-producto-update"),
    path("opciones-producto/<int:pk>/eliminar/", views.OpcionProductoDeleteView.as_view(), name="opcion-producto-delete"),
]
