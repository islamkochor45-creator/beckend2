from django.db import models
from django.conf import settings
from core.models import TimeStampedModel


class ChatRoomManager(models.Manager):
    def get_or_create_support_room(self, user):
        """
        Возвращает приватную комнату поддержки для конкретного пользователя.
        Если такой ещё нет — создаёт и сразу добавляет пользователя как participant.
        Комнату определяем по имени вида 'support_<user_id>', чтобы избежать
        дублей при повторных вызовах.
        """
        room_name = f"support_{user.id}"
        room = self.filter(name=room_name, participants=user).first()
        if room:
            return room, False
        room = self.create(name=room_name)
        room.participants.add(user)
        return room, True


class ChatRoom(models.Model):
    name = models.CharField(max_length=255)
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="chat_rooms"
    )

    objects = ChatRoomManager()

    def __str__(self):
        return self.name


class Message(TimeStampedModel):
    room = models.ForeignKey(
        ChatRoom, on_delete=models.CASCADE, related_name="messages"
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField()

    def __str__(self):
        return f"Message by {self.user.email} in {self.room.name}"
