import jwt
from urllib.parse import parse_qs
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import UntypedToken

from .models import ChatRoom, Message

User = get_user_model()


class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        params = parse_qs(self.scope["query_string"].decode())
        token = params.get("token", [None])[0]
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.group_name = f"chat_{self.room_name}"

        if token is None:
            await self.close()
            return

        user = await self.get_user(token)
        if user is None:
            await self.close()
            return

        self.scope["user"] = user
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive_json(self, content, **kwargs):
        text = content.get("text")
        if not text:
            return

        # Сохраняем сообщение в БД — без этого оно существовало только
        # как временная рассылка через Redis и терялось при обновлении
        # страницы/переподключении.
        await self.save_message(text)

        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "chat.message",
                "text": text,
                "user": self.scope["user"].email,
            },
        )

    async def chat_message(self, event):
        await self.send_json({"text": event["text"], "user": event["user"]})

    @database_sync_to_async
    def save_message(self, text):
        Message.objects.create(
            room_id=self.room_name,
            user=self.scope["user"],
            text=text,
        )

    @database_sync_to_async
    def get_user(self, token):
        try:
            UntypedToken(token)
            decoded_data = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user_id = decoded_data.get("user_id")
            return User.objects.filter(id=user_id).first()
        except Exception:
            return None
