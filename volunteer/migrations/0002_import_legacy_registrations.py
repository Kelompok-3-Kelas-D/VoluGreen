from django.db import migrations


STATUS_MAP = {
    "pending": "PENDING",
    "accepted": "ACCEPTED",
    "rejected": "REJECTED",
    "cancelled": "CANCELLED",
    "attended": "COMPLETED",
    "absent": "ABSENT",
}


def copy_legacy_registrations(apps, schema_editor):
    LegacyApplication = apps.get_model("relawan", "PendaftaranKegiatan")
    Application = apps.get_model("volunteer", "PendaftaranRelawan")
    Profile = apps.get_model("main", "Profile")
    db_alias = schema_editor.connection.alias

    for old in LegacyApplication.objects.using(db_alias).select_related("relawan").iterator():
        profile = Profile.objects.using(db_alias).filter(user_id=old.relawan_id).first()
        status = STATUS_MAP.get(old.status, "PENDING")
        application, created = Application.objects.using(db_alias).get_or_create(
            relawan_id=old.relawan_id,
            kegiatan_id=old.kegiatan_id,
            defaults={
                "status": status,
                "motivasi": "Pendaftaran dari versi sebelumnya.",
                "kontak_darurat": (profile.phone_number if profile and profile.phone_number else "Belum diisi"),
                "pesan": old.pesan or "",
                "hadir": status == "COMPLETED",
            },
        )
        if created and old.dibuat_pada:
            application.waktu_daftar = old.dibuat_pada
            application.save(using=db_alias, update_fields=["waktu_daftar"])


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0003_profile"),
        ("organizer", "0002_alter_kegiatan_kategori_delete_kategori"),
        ("relawan", "0001_initial"),
        ("volunteer", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(copy_legacy_registrations, migrations.RunPython.noop),
    ]
