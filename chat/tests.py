from asgiref.sync import async_to_sync
from django.test import SimpleTestCase

from chat.consumers import ChatConsumer


class DummyChannelLayer:
    def __init__(self):
        self.sent = []

    async def group_send(self, group_name, message):
        self.sent.append({"group_name": group_name, **message})


class ChatConsumerMessageContractTests(SimpleTestCase):
    def test_receive_json_normalizes_text_key(self):
        consumer = ChatConsumer()
        consumer.scope = {
            "user": type("User", (), {"email": "alice@example.com"})(),
            "url_route": {"kwargs": {"room_name": "room-1"}},
        }
        consumer.room_name = "room-1"
        consumer.group_name = "chat_room-1"
        consumer.channel_name = "channel-1"
        consumer.channel_layer = DummyChannelLayer()

        async def fake_get_room_by_name(room_name):
            return type("Room", (), {"id": 1, "name": room_name})()

        async def fake_create_message(room, user, text):
            return None

        consumer.get_room_by_name = fake_get_room_by_name
        consumer.create_message = fake_create_message

        async_to_sync(consumer.receive_json)({"text": "hello from text key"})

        self.assertEqual(len(consumer.channel_layer.sent), 1)
        self.assertEqual(consumer.channel_layer.sent[0]["text"], "hello from text key")
        self.assertEqual(
            consumer.channel_layer.sent[0]["sender_channel_name"], "channel-1"
        )
        self.assertNotIn("message", consumer.channel_layer.sent[0])

    def test_receive_json_accepts_legacy_message_key(self):
        consumer = ChatConsumer()
        consumer.scope = {
            "user": type("User", (), {"email": "bob@example.com"})(),
            "url_route": {"kwargs": {"room_name": "room-2"}},
        }
        consumer.room_name = "room-2"
        consumer.group_name = "chat_room-2"
        consumer.channel_name = "channel-2"
        consumer.channel_layer = DummyChannelLayer()

        async def fake_get_room_by_name(room_name):
            return type("Room", (), {"id": 2, "name": room_name})()

        async def fake_create_message(room, user, text):
            return None

        consumer.get_room_by_name = fake_get_room_by_name
        consumer.create_message = fake_create_message

        async_to_sync(consumer.receive_json)({"message": "legacy payload"})

        self.assertEqual(len(consumer.channel_layer.sent), 1)
        self.assertEqual(consumer.channel_layer.sent[0]["text"], "legacy payload")
        self.assertEqual(
            consumer.channel_layer.sent[0]["sender_channel_name"], "channel-2"
        )
        self.assertNotIn("message", consumer.channel_layer.sent[0])

    def test_chat_message_ignores_sender_channel(self):
        consumer = ChatConsumer()
        consumer.channel_name = "self-channel"
        consumer.send_json = lambda payload: (_ for _ in ()).throw(
            AssertionError("self echo should be ignored")
        )

        async_to_sync(consumer.chat_message)(
            {"text": "hello", "user": "me", "sender_channel_name": "self-channel"}
        )
