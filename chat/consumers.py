import json
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from authentication.models import User

from .models import Message


class ChatConsumer(AsyncWebsocketConsumer):
    user = None
    other_user = None

    async def connect(self):
        self.user = self.scope["user"]
        self.other_user_id = int(self.scope["url_route"]["kwargs"]["other_user_id"])

        # Check if the user is authenticated and is either a lecturer or class rep
        if not self.user.is_authenticated or not (
            self.user.is_lecturer or self.user.is_class_rep
        ):
            await self.close()
            return

        # Fetch the other user from the database using user_id
        self.other_user = await self.get_user(self.other_user_id)

        # Ensure that the other user is either a lecturer or class rep, opposite to the current user
        if not self.is_valid_chat_participant():
            await self.close()
            return

        self.room_name = f"room_{min(self.user.id, self.other_user.id)}_{max(self.user.id, self.other_user.id)}"
        self.room_group_name = f"chat_{self.room_name}"

        # Enter chat room
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

        # Send previous messages
        await self.send_previous_messages()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_text = text_data_json["message"]

        # Save the message to the database
        message: Message = await self.save_message(
            self.user.id, self.other_user.id, message_text
        )
        timestamp = message.timestamp.strftime("%Y-%m-%d %H:%M:%S")

        # Broadcast the message to the group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat.message",
                "message": message_text,
                "sender_id": self.user.id,
                "recipient_id": self.other_user.id,
                "timestamp": timestamp,
            },
        )

    async def chat_message(self, event):
        message = event["message"]
        sender_id = event["sender_id"]
        recipient_id = event["recipient_id"]
        timestamp = event["timestamp"]

        await self.send(
            text_data=json.dumps(
                {
                    "message": message,
                    "sender_id": sender_id,
                    "recipient_id": recipient_id,
                    "timestamp": timestamp,
                }
            )
        )

    async def send_previous_messages(self):
        """Send the previous chat messages between the users when the connection is established."""
        messages: list[Message] = await self.get_previous_messages(
            self.user.id, self.other_user.id
        )
        message_list = [
            {
                "sender_id": message.sender.id,
                "recipient_id": message.recipient.id,
                "text": message.text,
                "timestamp": message.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            }
            for message in messages
        ]
        await self.send(text_data=json.dumps(message_list))

    @database_sync_to_async
    def get_user(self, user_id: int) -> User:
        """Fetch the user from the database."""
        return User.objects.filter(pk=user_id).first()

    @database_sync_to_async
    def save_message(self, sender_id, recipient_id, text) -> Message:
        sender = User.objects.get(pk=sender_id)
        recipient = User.objects.get(pk=recipient_id)
        return Message.objects.create(sender=sender, recipient=recipient, text=text)

    @database_sync_to_async
    def get_previous_messages(self, user1_id, user2_id):
        """Fetch previous messages between the two users."""
        return Message.objects.filter(
            sender_id__in=[user1_id, user2_id],
            recipient_id__in=[user1_id, user2_id],
        ).order_by("timestamp")

    def is_valid_chat_participant(self):
        """Check that both users are valid participants in this chat."""
        # Ensure the other user exists and is either a lecturer or a class rep
        if not self.other_user:
            return False

        # The current user must be chatting with someone with an opposite role
        if self.user.is_lecturer and self.other_user.is_class_rep:
            return True
        if self.user.is_class_rep and self.other_user.is_lecturer:
            return True

        return False
