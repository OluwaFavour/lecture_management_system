from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


# Create your models here.
class Notification(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    creator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications",
        limit_choices_to={"is_class_rep": True},
    )
    read_by = models.ManyToManyField(
        User,
        related_name="read_notifications",
        blank=True,
        limit_choices_to={"is_lecturer": False},
    )

    def __str__(self):
        return self.title

    @property
    def recipients(self):
        return User.objects.filter(is_lecturer=False, level=self.creator.level)

    @property
    def is_read(self):
        return self.read_by.exists()

    @property
    def is_unread(self):
        return not self.is_read

    @property
    def is_read_by_student(self, student):
        return self.read_by.filter(pk=student.pk).exists()

    @property
    def is_unread_by_student(self, student):
        return not self.is_read_by_student(student)

    def mark_as_read(self, student):
        self.read_by.add(student)

    def mark_as_unread(self, student):
        if self.is_read_by_student(student):
            self.read_by.remove(student)
