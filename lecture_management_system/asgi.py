"""
ASGI config for lecture_management_system project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from channels.sessions import SessionMiddlewareStack

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lecture_management_system.settings")
asgi_app = get_asgi_application()

from chat.routing import websocket_urlpatterns
from chat.middleware import SessionAuthMiddleware

application = ProtocolTypeRouter(
    {
        "http": asgi_app,
        "websocket": AllowedHostsOriginValidator(
            SessionAuthMiddleware(URLRouter(websocket_urlpatterns))
        ),
    }
)
