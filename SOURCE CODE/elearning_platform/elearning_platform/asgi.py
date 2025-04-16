"""
ASGI config for elearning_platform project.
It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
from . import routing

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "elearning_platform.settings")

# Application routing
application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                # Import URL patterns from routing.py
                routing.websocket_urlpatterns
            )
        )
    ),
})
