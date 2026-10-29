from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from main.models import Category, Profile
from organizer.models import Kegiatan


class PublishedActivityDirectoryTests(TestCase):
    def setUp(self):
        organizer = get_user_model().objects.create_user(
            username="directory-organizer@example.test",
            email="directory-organizer@example.test",
            password="test-password",
        )
        Profile.objects.create(
            user=organizer,
            role=Profile.Role.ORGANIZER,
            phone_number="081234567890",
            organization_name="Komunitas Direktori",
        )
        category = Category.objects.create(name="Kategori Direktori Uji")
        self.past_activity = Kegiatan.objects.create(
            organizer=organizer,
            kategori=category,
            nama="Kegiatan yang sudah dimulai",
            deskripsi="Aksi lingkungan sebelumnya.",
            tanggal_mulai=timezone.now() - timedelta(hours=1),
            nama_lokasi="Depok",
            kota="Depok",
            kuota=10,
            status_publikasi=Kegiatan.StatusPublikasi.PUBLISHED,
        )
        self.future_activity = Kegiatan.objects.create(
            organizer=organizer,
            kategori=category,
            nama="Kegiatan mendatang",
            deskripsi="Aksi lingkungan berikutnya.",
            tanggal_mulai=timezone.now() + timedelta(days=1),
            nama_lokasi="Bandung",
            kota="Bandung",
            kuota=10,
            status_publikasi=Kegiatan.StatusPublikasi.PUBLISHED,
        )

    def test_published_past_activity_is_visible_without_registration_link(self):
        response = self.client.get(reverse("eksplorasi:index"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Kegiatan yang sudah dimulai")
        self.assertContains(response, 'id="kegiatan-sebelumnya"')
        self.assertContains(response, "Waktu mulai sudah lewat; pendaftaran ditutup.")
        self.assertNotContains(
            response,
            reverse("volunteer:halaman_daftar_kegiatan", args=[self.past_activity.pk]),
        )
        self.assertContains(
            response,
            reverse("volunteer:halaman_daftar_kegiatan", args=[self.future_activity.pk]),
        )

    def test_city_filter_can_find_published_past_activity(self):
        response = self.client.get(reverse("eksplorasi:index"), {"kota": "Depok"})

        self.assertContains(response, "Kegiatan yang sudah dimulai")
        self.assertNotContains(response, "<h3>Kegiatan mendatang</h3>")
