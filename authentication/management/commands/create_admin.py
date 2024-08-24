from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


User = get_user_model()


class Command(BaseCommand):
    help = "Create an admin user"

    def handle(self, *args, **kwargs):
        email = settings.ADMIN_EMAIL
        password = settings.ADMIN_PASSWORD
        if not User.objects.filter(email=email).exists():
            User.objects.create_superuser(
                email=email,
                password=password,
            )
            self.stdout.write(self.style.SUCCESS("Admin created successfully"))
        else:
            user = User.objects.get(email=email)
            user.is_superuser = True
            user.is_staff = True
            user.set_password(password)
            user.save()
            self.stdout.write(
                self.style.WARNING(
                    "Admin already exists, updated successfully with new password"
                )
            )
