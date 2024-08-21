from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path(
        "ws/chat/<str:lecturer_id>/<str:class_rep_id>/",
        consumers.ChatConsumer.as_asgi(),
    ),
]
