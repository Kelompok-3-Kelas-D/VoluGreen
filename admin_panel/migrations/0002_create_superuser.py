from django.db import migrations


def create_or_update_superuser(apps, schema_editor):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    # 1. Pastikan superuser admin / admin12345
    user, _ = User.objects.get_or_create(username="admin", defaults={"email": "admin@volugreen.local"})
    user.set_password("admin12345")
    user.is_staff = True
    user.is_superuser = True
    user.is_active = True
    user.save()

    # 2. Pastikan volugreenadmin / admin12345 juga jadi superuser
    user2, _ = User.objects.get_or_create(username="volugreenadmin", defaults={"email": "admin2@volugreen.local"})
    user2.set_password("admin12345")
    user2.is_staff = True
    user2.is_superuser = True
    user2.is_active = True
    user2.save()


def reverse_superuser(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('admin_panel', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_or_update_superuser, reverse_superuser),
    ]
