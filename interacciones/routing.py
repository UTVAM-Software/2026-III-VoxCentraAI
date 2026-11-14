from django.urls import re_path
from interacciones.consumers import CallConsumer, OrderUpdatesConsumer

websocket_urlpatterns = [
    re_path(r"^ws/call/$", CallConsumer.as_asgi()),
    re_path(r"^ws/orders/$", OrderUpdatesConsumer.as_asgi()),
]
