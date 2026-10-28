from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("main", "0003_profile"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.CreateModel(
                    name="ActivityModeration",
                    fields=[
                        ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                        ("title", models.CharField(max_length=160)),
                        ("organizer_name", models.CharField(max_length=160)),
                        ("description", models.TextField(blank=True)),
                        ("event_date", models.DateField(blank=True, null=True)),
                        ("location", models.CharField(blank=True, max_length=200)),
                        ("status", models.CharField(choices=[("pending", "Menunggu tinjauan"), ("approved", "Disetujui"), ("rejected", "Ditolak")], default="pending", max_length=12)),
                        ("moderator_note", models.TextField(blank=True)),
                        ("reviewed_at", models.DateTimeField(blank=True, null=True)),
                        ("created_at", models.DateTimeField(auto_now_add=True)),
                        ("category", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="activities", to="main.category")),
                        ("reviewed_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                    ],
                    options={
                        "verbose_name": "activity moderation record",
                        "verbose_name_plural": "activity moderation records",
                        "ordering": ["status", "-created_at"],
                        "db_table": "main_activitymoderation",
                    },
                ),
                migrations.CreateModel(
                    name="UserReport",
                    fields=[
                        ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                        ("reporter", models.CharField(max_length=160)),
                        ("subject", models.CharField(max_length=200)),
                        ("details", models.TextField()),
                        ("status", models.CharField(choices=[("open", "Baru"), ("reviewing", "Ditinjau"), ("resolved", "Selesai")], default="open", max_length=12)),
                        ("created_at", models.DateTimeField(auto_now_add=True)),
                    ],
                    options={
                        "ordering": ["status", "-created_at"],
                        "db_table": "main_userreport",
                    },
                ),
            ],
        ),
    ]
