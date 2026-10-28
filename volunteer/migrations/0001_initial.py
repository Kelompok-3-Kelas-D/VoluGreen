# Initial schema for the volunteer application.

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('organizer', '0002_alter_kegiatan_kategori_delete_kategori'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='PendaftaranRelawan',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('status', models.CharField(choices=[('PENDING', 'Menunggu Konfirmasi'), ('ACCEPTED', 'Diterima'), ('REJECTED', 'Ditolak'), ('CANCELLED', 'Dibatalkan'), ('COMPLETED', 'Selesai Berpartisipasi'), ('ABSENT', 'Tidak Hadir')], db_index=True, default='PENDING', max_length=10)),
                ('motivasi', models.TextField()),
                ('kontak_darurat', models.CharField(max_length=30)),
                ('pengalaman_relevan', models.TextField(blank=True, default='')),
                ('kebutuhan_khusus', models.CharField(blank=True, default='', max_length=255)),
                ('pesan', models.CharField(blank=True, default='', max_length=500)),
                ('alasan_pembatalan', models.TextField(blank=True, default='')),
                ('waktu_pembatalan', models.DateTimeField(blank=True, null=True)),
                ('hadir', models.BooleanField(default=False)),
                ('jam_kontribusi', models.PositiveIntegerField(default=0)),
                ('catatan_dampak', models.TextField(blank=True, default='')),
                ('refleksi_relawan', models.TextField(blank=True, default='')),
                ('waktu_selesai_partisipasi', models.DateTimeField(blank=True, null=True)),
                ('waktu_daftar', models.DateTimeField(auto_now_add=True)),
                ('waktu_diperbarui', models.DateTimeField(auto_now=True)),
                ('kegiatan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pendaftaran_volunteer', to='organizer.kegiatan')),
                ('relawan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pendaftaran_relawan', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'pendaftaran relawan',
                'verbose_name_plural': 'pendaftaran relawan',
                'ordering': ['-waktu_daftar'],
                'indexes': [models.Index(fields=['relawan', 'status'], name='volunteer_rel_status_idx')],
                'constraints': [models.UniqueConstraint(fields=('relawan', 'kegiatan'), name='unique_relawan_per_kegiatan')],
            },
        ),
    ]
