from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create or reset a default superuser."

    def handle(self, *args, **options):
        User = get_user_model()
        username = "admin"
        password = "admin12345"

        user, created = User.objects.get_or_create(
            username=username,
            defaults={"email": "admin@volugreen.local"}
        )
        user.set_password(password)
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.save()

        if created:
            self.stdout.write(self.style.SUCCESS(f"Superuser '{username}' created successfully."))
        else:
            self.stdout.write(self.style.SUCCESS(f"Superuser '{username}' updated with valid credentials."))
