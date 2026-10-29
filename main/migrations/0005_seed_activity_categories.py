from django.db import migrations


DEFAULT_CATEGORIES = (
    ("Aksi Bersih Pantai dan Sungai", "Pembersihan pantai, sungai, dan kawasan perairan."),
    ("Penanaman Mangrove", "Penanaman dan perawatan mangrove di kawasan pesisir."),
    ("Pengelolaan Sampah", "Pemilahan sampah, daur ulang, dan kegiatan bank sampah."),
    ("Pertanian Perkotaan", "Berkebun dan menanam pangan di lingkungan perkotaan."),
    ("Edukasi Lingkungan", "Kampanye dan kegiatan belajar tentang lingkungan."),
    ("Konservasi Alam", "Perlindungan habitat dan keanekaragaman hayati."),
)


def add_default_categories(apps, schema_editor):
    Category = apps.get_model("main", "Category")
    database = schema_editor.connection.alias
    categories = Category.objects.using(database)
    for name, description in DEFAULT_CATEGORIES:
        if not categories.filter(name__iexact=name).exists():
            categories.create(name=name, description=description, is_active=True)


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0004_move_admin_models_to_admin_panel"),
    ]

    operations = [
        migrations.RunPython(add_default_categories, migrations.RunPython.noop),
    ]
