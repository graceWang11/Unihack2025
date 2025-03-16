"""
ASGI config for interview_platform project.
It exposes the ASGI callable as a module-level variable named ``application``.
For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""
import os
import django

# Ensure Django settings module is set before setup
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "interview_platform.settings")
django.setup()

# Import these after django.setup()
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from core.routing import websocket_urlpatterns

# Get the Django ASGI application
django_asgi_app = get_asgi_application()

# Create the ASGI application with both HTTP and WebSocket support
application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})