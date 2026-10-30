from django.contrib.auth.hashers import make_password
from django.db import migrations
from django.utils import timezone


def create_or_update_superuser(apps, schema_editor):
    User = apps.get_model("auth", "User")
    db = schema_editor.connection.alias

    for username, email in [
        ("admin", "admin@volugreen.local"),
        ("volugreenadmin", "admin2@volugreen.local"),
    ]:
        user, _ = User.objects.using(db).get_or_create(
            username=username,
            defaults={"email": email},
        )
        user.email = email
        user.password = make_password("admin12345")
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        # Some existing databases have this column marked NOT NULL.
        user.last_login = timezone.now()
        user.save(using=db)


def reverse_superuser(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("admin_panel", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(create_or_update_superuser, reverse_superuser),
    ]
