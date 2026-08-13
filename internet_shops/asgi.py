import os
import django
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from core.jwt_auth_middleware import JWTAuthMiddleware
import chat.routing

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "internet_shops.settings.dev")
django.setup()

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": JWTAuthMiddleware(URLRouter(chat.routing.websocket_urlpatterns)),
    }
)
