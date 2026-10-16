from django.urls import path

from . import views

app_name = "comercios"

urlpatterns = [
    path("", views.portada, name="portada"),
    path("comercios/", views.resumen, name="resumen"),
]
