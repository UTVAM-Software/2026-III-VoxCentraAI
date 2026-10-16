from django.urls import path

from . import views

app_name = "accesos"

urlpatterns = [path("", views.resumen, name="resumen")]
