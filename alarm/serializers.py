from rest_framework import serializers

from .models import Alert, AlertSettings

from courses.serializers import CourseSerializer


class AlertSerializer(serializers.ModelSerializer):
    event = CourseSerializer(read_only=True)

    class Meta:
        model = Alert
        exclude = ("students",)
        read_only_fields = ("timestamp", "is_active")


class AlertSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlertSettings
        fields = "__all__"
        read_only_fields = ("student",)

    def update(self, instance, validated_data):
        # Ensure that the student can only update their own alert settings
        if instance.student != self.context["request"].user:
            raise serializers.ValidationError(
                "You cannot update another student's alert settings"
            )

        # Update email alert settings
        if "via_email" in validated_data:
            if validated_data.pop("via_email"):
                instance.enable_email_alerts()
            else:
                instance.disable_email_alerts()

        # Update SMS alert settings
        if "via_sms" in validated_data:
            if validated_data.pop("via_sms"):
                instance.enable_sms_alerts()
            else:
                instance.disable_sms_alerts()

        # Save the instance to persist the changes
        instance.save()

        # Update other fields if necessary
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Save the instance again to persist other updates
        instance.save()

        return instance
