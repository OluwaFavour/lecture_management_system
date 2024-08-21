from django.contrib.auth import get_user_model
from django.db import models

# Create your models here.
# User = get_user_model()


# class Alarm(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="alarms")
#     title = models.CharField(max_length=255)
#     description = models.TextField()
#     timestamp = models.DateTimeField(auto_now_add=True)
#     is_active = models.BooleanField(default=True)
#     is_seen = models.BooleanField(default=False)

#     def mark_as_seen(self):
#         self.is_seen = True
#         self.save(update_fields=["is_seen"])
