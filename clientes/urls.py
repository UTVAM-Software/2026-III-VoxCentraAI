from django.urls import path

from clientes import views

app_name = "clientes"

urlpatterns = [
    path("", views.ClienteListView.as_view(), name="cliente-list"),
    path("nuevo/", views.ClienteCreateView.as_view(), name="cliente-create"),
    path("<int:pk>/editar/", views.ClienteUpdateView.as_view(), name="cliente-update"),
    path("<int:pk>/eliminar/", views.ClienteDeleteView.as_view(), name="cliente-delete"),
    path("direcciones/", views.DireccionClienteListView.as_view(), name="direccion-list"),
    path("direcciones/nueva/", views.DireccionClienteCreateView.as_view(), name="direccion-create"),
    path("direcciones/<int:pk>/editar/", views.DireccionClienteUpdateView.as_view(), name="direccion-update"),
    path("direcciones/<int:pk>/eliminar/", views.DireccionClienteDeleteView.as_view(), name="direccion-delete"),
]
