from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path(
        "ws/chat/<str:other_user_id>",
        consumers.ChatConsumer.as_asgi(),
    ),
]
