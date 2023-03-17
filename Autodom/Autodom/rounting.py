from django.urls import path
from .consumers import NotifConsumer

ws_urlpatterns = [
    path('ws/notif/',NotifConsumer.as_asgi())
    ]
