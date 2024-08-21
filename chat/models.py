from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Q
from django.utils import timezone

# Create your models here.
User = get_user_model()


class Message(models.Model):
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sent_messages",
        limit_choices_to=Q(is_lecturer=True) | Q(is_classrep=True),
    )
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="received_messages",
        limit_choices_to=Q(is_lecturer=True) | Q(is_classrep=True),
    )
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True)
    is_read = models.BooleanField(default=False)

    def mark_as_read(self):
        self.is_read = True
        self.read_at = timezone.now()
        self.save(update_fields=["is_read", "read_at"])
