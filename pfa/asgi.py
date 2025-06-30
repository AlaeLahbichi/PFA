"""
ASGI config for pfa project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter # type: ignore
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack # type: ignore
import tonapp.routing # type: ignore

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pfa.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            tonapp.routing.websocket_urlpatterns
        )
    ),
})


application = get_asgi_application()
