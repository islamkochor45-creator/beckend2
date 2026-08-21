from django.contrib import admin
from .models import ChatRoom, Message


@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ("name", "participant_count")
    filter_horizontal = ("participants",)  # удобный виджет: два списка + поиск
    search_fields = ("name", "participants__email")

    def participant_count(self, obj):
        return obj.participants.count()

    participant_count.short_description = "Участников"


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("room", "user", "text", "created_at")
    list_filter = ("room",)
    search_fields = ("text", "user__email")
