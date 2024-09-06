from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

User = get_user_model()


@receiver(post_save, sender=User)
def create_alert(sender, instance, **kwargs):
    from alarm.models import Alert, Course, AlertSettings

    # Create an alert setting for the user
    alert_settings, created = AlertSettings.objects.get_or_create(student=instance)
    if created:
        alert_settings.save()

    # Create an alert for the user if they are a student for all courses
    if not instance.is_lecturer:
        courses = Course.objects.all()
        for course in courses:
            alert, created = Alert.objects.get_or_create(
                event=course,
                defaults={
                    "title": f"{course.code} - {course.name}",
                    "description": f"Your {course.code} - {course.name} is starting soon",
                },
            )
            if created:
                alert.students.add(instance)
            elif not alert.students.filter(id=instance.id).exists():
                alert.students.add(instance)
