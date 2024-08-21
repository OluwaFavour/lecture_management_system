from rest_framework import serializers

from .models import Message


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = "__all__"


class PreviousMessages:
    def __init__(self, sent_messages, received_messages):
        self.sent_messages = sent_messages
        self.received_messages = received_messages


class PreviousMessagesSerializer(serializers.Serializer):
    sent_messages = MessageSerializer(many=True)
    received_messages = MessageSerializer(many=True)
