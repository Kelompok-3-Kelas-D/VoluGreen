"""
WSGI config for volugreen project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'volugreen.settings')

application = get_wsgi_application()


def _ensure_initial_data():
    try:
        from django.core.management import call_command
        call_command('seed_initial_activities')
    except Exception as exc:
        print(f"[WSGI BOOT] Seed failed: {exc}")

    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        admin_user, _ = User.objects.get_or_create(
            username="admin", defaults={"email": "admin@volugreen.local"}
        )
        admin_user.set_password("admin12345")
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.save()
    except Exception as exc:
        print(f"[WSGI BOOT] Admin creation failed: {exc}")


_ensure_initial_data()
