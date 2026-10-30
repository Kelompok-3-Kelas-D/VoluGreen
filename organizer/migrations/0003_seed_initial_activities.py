from django.core.management import call_command
from django.db import migrations


def run_seed(apps, schema_editor):
    try:
        call_command("seed_initial_activities")
    except Exception as exc:
        print(f"Migration seed warning: {exc}")


class Migration(migrations.Migration):

    dependencies = [
        ("organizer", "0002_alter_kegiatan_kategori_delete_kategori"),
        ("main", "0005_seed_activity_categories"),
    ]

    operations = [
        migrations.RunPython(run_seed, migrations.RunPython.noop),
    ]
