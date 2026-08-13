from urllib.parse import parse_qs

import jwt
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.conf import settings
from rest_framework_simplejwt.tokens import UntypedToken

User = get_user_model()


@database_sync_to_async
def get_user_from_token(token):
    try:
        UntypedToken(token)
        decoded_data = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id = decoded_data.get("user_id")
        user = User.objects.filter(id=user_id).first()
        if user is None:
            print(f"[JWTAuthMiddleware] user_id={user_id} not found in DB")
            return AnonymousUser()
        return user
    except Exception as e:
        # ВРЕМЕННО: выводим точную причину, почему токен не прошёл проверку
        print(f"[JWTAuthMiddleware] token rejected: {type(e).__name__}: {e}")
        return AnonymousUser()


class JWTAuthMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        query_string = parse_qs(scope.get("query_string", b"").decode())
        token = query_string.get("token", [None])[0]
        if not token:
            print("[JWTAuthMiddleware] no token in query string")
        scope["user"] = await get_user_from_token(token) if token else AnonymousUser()
        return await self.app(scope, receive, send)