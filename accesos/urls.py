from django.urls import path

from accesos.views import (
    AlcanceListView,
    alcance_create_view,
    alcance_delete_view,
    alcance_update_view,
    membresia_create_view,
    membresia_delete_view,
    membresia_update_view,
    MembresiaListView,
    rol_create_view,
    rol_delete_view,
    rol_update_view,
    RolListView,
)

app_name = "accesos"

urlpatterns = [
    path("roles-plataforma/", RolListView.as_view(), name="rol-list"),
    path("roles-plataforma/nuevo/", rol_create_view, name="rol-create"),
    path("roles-plataforma/<int:pk>/editar/", rol_update_view, name="rol-update"),
    path("roles-plataforma/<int:pk>/eliminar/", rol_delete_view, name="rol-delete"),
    path("membresias/", MembresiaListView.as_view(), name="membresia-list"),
    path("membresias/nueva/", membresia_create_view, name="membresia-create"),
    path("membresias/<int:pk>/editar/", membresia_update_view, name="membresia-update"),
    path("membresias/<int:pk>/eliminar/", membresia_delete_view, name="membresia-delete"),
    path("alcances-sucursal/", AlcanceListView.as_view(), name="alcance-list"),
    path("alcances-sucursal/nuevo/", alcance_create_view, name="alcance-create"),
    path(
        "alcances-sucursal/<int:membresia_id>/<int:sucursal_id>/editar/",
        alcance_update_view,
        name="alcance-update",
    ),
    path(
        "alcances-sucursal/<int:membresia_id>/<int:sucursal_id>/eliminar/",
        alcance_delete_view,
        name="alcance-delete",
    ),
]
