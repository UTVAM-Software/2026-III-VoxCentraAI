from django.urls import path

from interacciones.views import (
    InteraccionListView,
    interaccion_create_view,
    interaccion_delete_view,
    interaccion_update_view,
)

app_name = "interacciones"

urlpatterns = [
    path("", InteraccionListView.as_view(), name="interaccion-list"),
    path("nueva/", interaccion_create_view, name="interaccion-create"),
    path("<int:pk>/editar/", interaccion_update_view, name="interaccion-update"),
    path("<int:pk>/eliminar/", interaccion_delete_view, name="interaccion-delete"),
]
