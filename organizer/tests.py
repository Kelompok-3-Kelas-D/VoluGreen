from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from .models import DampakKegiatan, Kategori, Kegiatan


class KegiatanModelTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user("org1", password="x")
        self.kategori = Kategori.objects.create(nama="Bersih Lingkungan")

    def buat(self, **kw):
        data = dict(
            organizer=self.user,
            nama="Bersih Pantai",
            deskripsi="Aksi bersih pantai",
            kategori=self.kategori,
            tanggal_mulai=timezone.now() + timedelta(days=3),
            nama_lokasi="Pantai Ancol",
            kuota=20,
        )
        data.update(kw)
        return Kegiatan.objects.create(**data)

    def test_default_draft_dan_tanpa_koordinat(self):
        k = self.buat()
        self.assertEqual(k.status_publikasi, "draft")
        self.assertFalse(k.is_published)
        self.assertFalse(k.punya_koordinat)

    def test_koordinat_desimal(self):
        k = self.buat(latitude=Decimal("-6.402484"), longitude=Decimal("106.794243"))
        k.refresh_from_db()
        self.assertTrue(k.punya_koordinat)
        self.assertEqual(k.latitude, Decimal("-6.402484"))

    def test_validasi_koordinat_dan_kuota(self):
        k = self.buat()
        k.latitude, k.longitude, k.kuota = Decimal("95"), Decimal("200"), 0
        with self.assertRaises(ValidationError) as cm:
            k.full_clean()
        self.assertEqual({"latitude", "longitude", "kuota"}, set(cm.exception.message_dict))

    def test_sisa_kuota_tanpa_modul_pendaftaran(self):
        self.assertEqual(self.buat(kuota=5).sisa_kuota, 5)

    def test_kepemilikan(self):
        k = self.buat()
        lain = get_user_model().objects.create_user("org2", password="x")
        self.assertTrue(k.dikelola_oleh(self.user))
        self.assertFalse(k.dikelola_oleh(lain))

    def test_dampak_one_to_one(self):
        k = self.buat()
        DampakKegiatan.objects.create(kegiatan=k, sampah_terkumpul_kg=12.5)
        self.assertEqual(k.dampak.pohon_ditanam, 0)
