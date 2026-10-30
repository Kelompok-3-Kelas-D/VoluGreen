from django.db import migrations


def import_saved_activities(apps, schema_editor):
    KoleksiKegiatan = apps.get_model("eksplorasi", "KoleksiKegiatan")
    ArsipKegiatan = apps.get_model("eksplorasi", "ArsipKegiatan")
    database = schema_editor.connection.alias
    seen = set()
    archives = []
    for collection in KoleksiKegiatan.objects.using(database).all().iterator():
        for activity_id in collection.kegiatan.using(database).values_list("pk", flat=True):
            pair = (collection.pengguna_id, activity_id)
            if pair not in seen:
                seen.add(pair)
                archives.append(ArsipKegiatan(pengguna_id=pair[0], kegiatan_id=pair[1]))
    ArsipKegiatan.objects.using(database).bulk_create(archives, ignore_conflicts=True)


class Migration(migrations.Migration):
    dependencies = [("eksplorasi", "0002_arsipkegiatan")]
    operations = [migrations.RunPython(import_saved_activities, migrations.RunPython.noop)]
