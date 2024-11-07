import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import scannerpro.routing  # Update with the app name

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'moderntrade.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            scannerpro.routing.websocket_urlpatterns  # Update with the app name
        )
    ),
})
