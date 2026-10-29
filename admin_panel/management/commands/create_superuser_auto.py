from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create a default superuser if none exists."

    def handle(self, *args, **options):
        User = get_user_model()
        username = "admin"
        password = "admin12345"

        if User.objects.filter(is_superuser=True).exists():
            self.stdout.write(self.style.WARNING("Superuser already exists — skipping."))
            return

        User.objects.create_superuser(username=username, email="", password=password)
        self.stdout.write(self.style.SUCCESS(f"Superuser '{username}' created successfully."))
