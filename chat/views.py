from rest_framework import generics, permissions
from rest_framework.response import Response
from .models import ChatRoom, Message
from .serializers import ChatRoomSerializer, MessageSerializer


class ChatRoomListView(generics.ListCreateAPIView):
    serializer_class = ChatRoomSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Обычный пользователь видит только комнаты, в которых он participant.
        # Админ/staff видит все комнаты (нужно для панели поддержки).
        user = self.request.user
        if user.is_staff:
            return ChatRoom.objects.all()
        return ChatRoom.objects.filter(participants=user)

    def list(self, request, *args, **kwargs):
        # get-or-create: если у обычного пользователя ещё нет своей комнаты
        # поддержки — создаём её автоматически при первом обращении.
        user = request.user
        if not user.is_staff:
            room, created = ChatRoom.objects.get_or_create_support_room(user)
        response = super().list(request, *args, **kwargs)
        return response

    def perform_create(self, serializer):
        room = serializer.save()
        room.participants.add(self.request.user)


class MessageListView(generics.ListCreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_room(self):
        room_id = self.kwargs["room_id"]
        user = self.request.user
        if user.is_staff:
            return ChatRoom.objects.get(id=room_id)
        # обычный юзер может читать/писать только в свою комнату
        return ChatRoom.objects.get(id=room_id, participants=user)

    def get_queryset(self):
        room = self.get_room()
        return Message.objects.filter(room=room)

    def perform_create(self, serializer):
        room = self.get_room()
        serializer.save(user=self.request.user, room=room)
