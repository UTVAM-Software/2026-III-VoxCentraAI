from django.urls import path

from comercios import views

app_name = "comercios"

urlpatterns = [
    path("", views.ComercioListView.as_view(), name="comercio-list"),
    path("comercios/nuevo/", views.ComercioCreateView.as_view(), name="comercio-create"),
    path("comercios/<int:pk>/editar/", views.ComercioUpdateView.as_view(), name="comercio-update"),
    path("comercios/<int:pk>/eliminar/", views.ComercioDeleteView.as_view(), name="comercio-delete"),
    path("sucursales/", views.SucursalListView.as_view(), name="sucursal-list"),
    path("sucursales/nueva/", views.SucursalCreateView.as_view(), name="sucursal-create"),
    path("sucursales/<int:pk>/editar/", views.SucursalUpdateView.as_view(), name="sucursal-update"),
    path("sucursales/<int:pk>/eliminar/", views.SucursalDeleteView.as_view(), name="sucursal-delete"),
    path("configuraciones/", views.ConfiguracionListView.as_view(), name="configuracion-list"),
    path("configuraciones/nueva/", views.ConfiguracionCreateView.as_view(), name="configuracion-create"),
    path("configuraciones/<int:pk>/editar/", views.ConfiguracionUpdateView.as_view(), name="configuracion-update"),
    path("configuraciones/<int:pk>/eliminar/", views.ConfiguracionDeleteView.as_view(), name="configuracion-delete"),
]
