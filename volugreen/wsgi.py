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


# --- Auto-create superuser on server boot ---
def _ensure_superuser():
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()

        username = "admin"
        password = "admin12345"

        user, created = User.objects.get_or_create(
            username=username,
            defaults={"email": "admin@volugreen.local"},
        )
        user.set_password(password)
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.save()

        if created:
            print(f"[WSGI BOOT] Superuser '{username}' CREATED.")
        else:
            print(f"[WSGI BOOT] Superuser '{username}' password RESET.")
    except Exception as exc:
        print(f"[WSGI BOOT] Superuser creation failed: {exc}")


_ensure_superuser()
