from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("admin_panel", "0001_initial"),
        ("main", "0003_profile"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.DeleteModel(name="ActivityModeration"),
                migrations.DeleteModel(name="UserReport"),
            ],
        ),
    ]
