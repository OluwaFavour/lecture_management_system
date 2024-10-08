from rest_framework import serializers

from .models import Notification
from authentication.serializers import StudentSerializer


class NotificationSerializer(serializers.ModelSerializer):
    creator = StudentSerializer(read_only=True)
    read_by = StudentSerializer(read_only=True, many=True)

    class Meta:
        model = Notification
        fields = "__all__"
        read_only_fields = ["creator", "read_by", "created_at", "updated_at"]
        depth = 1

    def create(self, validated_data):
        validated_data["creator"] = self.context["request"].user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)
