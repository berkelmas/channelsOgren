# chat/routing.py
from django.urls import path

from . import consumers

websocket_urlpatterns = [
    path('chat/<room_name>/', consumers.ChatConsumer),
]

