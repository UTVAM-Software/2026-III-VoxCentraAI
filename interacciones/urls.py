from django.urls import path

from . import views

app_name = "interacciones"

urlpatterns = [path("", views.resumen, name="resumen")]
