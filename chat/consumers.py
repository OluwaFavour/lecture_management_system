import json
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from .models import Message, User


class ChatConsumer(AsyncWebsocketConsumer):
    lecturer_id = None
    class_rep_id = None

    async def connect(self):
        self.user = self.scope["user"]
        self.lecturer_id = int(self.scope["url_route"]["kwargs"]["lecturer_id"])
        self.class_rep_id = int(self.scope["url_route"]["kwargs"]["class_rep_id"])

        # Check if the user is authenticated
        if not self.user.is_authenticated or self.user.is_anonymous:
            await self.close()
            return

        # Check if the lecturer_id and class_rep_id are valid
        if not await self.check_id(
            self.lecturer_id, role="lecturer"
        ) or not await self.check_id(self.class_rep_id, role="class_rep"):
            await self.close()
            return

        self.room_name = f"room_{self.lecturer_id}_{self.class_rep_id}"
        self.room_group_name = f"chat_{self.room_name}"

        # Enter chat room
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

        # Send previous messages
        message_list = []
        messages: list[Message] = await self.get_previous_messages(
            self.lecturer_id, self.class_rep_id
        )
        for message in messages:
            message_list.append(
                {
                    "sender_id": message.sender.id,
                    "recipient_id": message.recipient.id,
                    "text": message.text,
                    "timestamp": message.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                }
            )
        await self.send(text_data=json.dumps({message_list}))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        sender_id = text_data_json["sender_id"]
        recipient_id = text_data_json["recipient_id"]

        # Check if the sender_id and recipient_id are valid
        if sender_id == recipient_id:
            await self.close(reason="sender_id and recipient_id cannot be the same")
            return
        if sender_id not in [
            self.lecturer_id,
            self.class_rep_id,
        ] or recipient_id not in [
            self.lecturer_id,
            self.class_rep_id,
        ]:
            await self.close(reason="Invalid sender_id or recipient_id")
            return

        # Save message to the database
        message: Message = await self.save_message(sender_id, recipient_id, message)
        timestamp = message.timestamp.strftime("%Y-%m-%d %H:%M:%S")

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat.message",
                "message": message,
                "sender_id": sender_id,
                "recipient_id": recipient_id,
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

    @database_sync_to_async
    def save_message(self, sender_id, recipient_id, text) -> Message:
        sender = User.objects.get(pk=sender_id)
        recipient = User.objects.get(pk=recipient_id)
        return Message.objects.create(sender=sender, recipient=recipient, text=text)

    @database_sync_to_async
    def check_id(self, id, role=None):
        if role == "lecturer":
            return User.objects.filter(id=id, is_lecturer=True).exists()
        elif role == "class_rep":
            return User.objects.filter(
                id=id, is_student=True, is_class_rep=True
            ).exists()
        else:
            return User.objects.filter(id=id).exists()

    @database_sync_to_async
    def get_previous_messages(self, lecturer_id, class_rep_id):
        messages = Message.objects.filter(
            sender_id__in=[lecturer_id, class_rep_id],
            recipient_id__in=[lecturer_id, class_rep_id],
        ).order_by("timestamp")

        return messages
