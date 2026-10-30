from django.contrib.auth.hashers import check_password, make_password
from django.db import migrations


def disable_known_passwords(apps, schema_editor):
    User = apps.get_model("auth", "User")
    database = schema_editor.connection.alias
    for user in User.objects.using(database).filter(username__in=("admin", "volugreenadmin")):
        if check_password("admin12345", user.password):
            user.password = make_password(None)
            user.save(using=database, update_fields=["password"])


class Migration(migrations.Migration):
    dependencies = [("admin_panel", "0002_create_superuser")]
    operations = [migrations.RunPython(disable_known_passwords, migrations.RunPython.noop)]
