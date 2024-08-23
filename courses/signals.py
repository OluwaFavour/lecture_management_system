from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from courses.models import Course


User = get_user_model()


@receiver(post_save, sender=Course)
def create_alert(sender, instance: Course, **kwargs):
    from alarm.models import Alert

    # Create an alert for the course for all students
    students = User.objects.filter(is_lecturer=False)

    # Check if the alert already exists
    alert, created = Alert.objects.get_or_create(
        event=instance,
        defaults={
            "title": f"{instance.code} - {instance.name}",
            "description": f"Your {instance.code} - {instance.name} is starting soon",
        },
    )

    if created:
        # If the alert was just created, add all students in bulk
        alert.students.set(students)
    else:
        # Otherwise, add any students who are not already associated with the alert
        existing_students = alert.students.values_list("id", flat=True)
        new_students = students.exclude(id__in=existing_students)
        alert.students.add(*new_students)
