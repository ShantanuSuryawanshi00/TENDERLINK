from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os

class Command(BaseCommand):
    help = "Create superuser automatically if it does not exist"

    def handle(self, *args, **kwargs):
        User = get_user_model()
        username = os.environ.get("SUPERUSER_NAME", "admin")
        email = os.environ.get("SUPERUSER_EMAIL", "admin@example.com")
        password = os.environ.get("SUPERUSER_PASSWORD", "admin123")

        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(username=username, email=email, password=password)
            self.stdout.write(self.style.SUCCESS(f"Superuser '{username}' created"))
        else:
            self.stdout.write(f"Superuser '{username}' already exists")
