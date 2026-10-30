from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from main.models import Category, Profile
from organizer.models import Kegiatan
from .models import ArsipKegiatan


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
        self.volunteer = get_user_model().objects.create_user(
            username="directory-volunteer@example.test",
            email="directory-volunteer@example.test",
            password="test-password",
        )
        Profile.objects.create(
            user=self.volunteer,
            role=Profile.Role.VOLUNTEER,
            phone_number="081234567891",
            city="Depok",
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

    def test_anonymous_visitor_is_sent_to_login_before_exploration(self):
        response = self.client.get(reverse("eksplorasi:index"))

        self.assertRedirects(
            response,
            f"{reverse('main:login')}?next={reverse('eksplorasi:index')}",
        )

    def test_published_past_activity_is_visible_without_registration_link(self):
        self.client.force_login(self.volunteer)
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
        self.client.force_login(self.volunteer)
        response = self.client.get(reverse("eksplorasi:index"), {"kota": "Depok"})

        self.assertContains(response, "Kegiatan yang sudah dimulai")
        self.assertNotContains(response, "<h3>Kegiatan mendatang</h3>")

    def test_map_has_usable_location_links_when_tiles_fail(self):
        self.future_activity.latitude = Decimal("-6.402484")
        self.future_activity.longitude = Decimal("106.794243")
        self.future_activity.save(update_fields=["latitude", "longitude"])
        self.client.force_login(self.volunteer)
        response = self.client.get(reverse("eksplorasi:index"))
        self.assertContains(response, 'id="activity-map-fallback"')
        self.assertContains(response, self.future_activity.nama)
        self.assertContains(response, "https://www.openstreetmap.org/?mlat=-6.402484")
        detail = self.client.get(reverse("eksplorasi:detail", args=[self.future_activity.pk]))
        self.assertContains(detail, 'data-lat="-6.402484"')
        self.assertContains(detail, 'data-lng="106.794243"')
        self.assertContains(detail, "https://www.openstreetmap.org/?mlat=-6.402484")

    def test_map_explains_when_no_activity_has_coordinates(self):
        self.client.force_login(self.volunteer)
        response = self.client.get(reverse("eksplorasi:index"))
        self.assertNotContains(response, 'id="activity-map"')
        self.assertContains(response, "Belum ada kegiatan mendatang dengan koordinat")

    def test_detail_has_registration_action_for_volunteer(self):
        self.client.force_login(self.volunteer)
        response = self.client.get(reverse("eksplorasi:detail", args=[self.future_activity.pk]))
        self.assertContains(response, reverse("volunteer:halaman_daftar_kegiatan", args=[self.future_activity.pk]))
        self.assertContains(response, "Ikuti kegiatan")

    def test_past_detail_does_not_offer_registration(self):
        response = self.client.get(reverse("eksplorasi:detail", args=[self.past_activity.pk]))
        self.assertContains(response, "pendaftaran ditutup")
        self.assertNotContains(response, reverse("volunteer:halaman_daftar_kegiatan", args=[self.past_activity.pk]))

    def test_detail_returns_to_filtered_directory(self):
        self.client.force_login(self.volunteer)
        response = self.client.get(reverse("eksplorasi:detail", args=[self.future_activity.pk]), {
            "kembali": "/eksplorasi/?kota=Bandung",
        })
        self.assertContains(response, 'href="/eksplorasi/?kota=Bandung#kegiatan"')

    def test_volunteer_can_archive_and_remove_activity_from_archive_page(self):
        self.client.force_login(self.volunteer)
        url = reverse("eksplorasi:arsip_toggle", args=[self.future_activity.pk])
        response = self.client.post(url, {"next": reverse("eksplorasi:index")})
        self.assertRedirects(response, reverse("eksplorasi:index"))
        self.assertTrue(ArsipKegiatan.objects.filter(
            pengguna=self.volunteer, kegiatan=self.future_activity
        ).exists())
        directory = self.client.get(reverse("eksplorasi:index"))
        self.assertContains(directory, "Hapus dari arsip")
        self.assertContains(directory, 'aria-pressed="true"')
        self.assertContains(directory, f'href="{reverse("eksplorasi:arsip_daftar")}">Arsip kegiatan</a>')
        profile = self.client.get(reverse("main:profile_settings"))
        self.assertNotContains(profile, 'id="arsip"')
        archive_page = self.client.get(reverse("eksplorasi:arsip_daftar"))
        self.assertContains(archive_page, self.future_activity.nama)

        self.client.post(url, {"next": reverse("eksplorasi:arsip_daftar")})
        self.assertFalse(ArsipKegiatan.objects.filter(
            pengguna=self.volunteer, kegiatan=self.future_activity
        ).exists())

    def test_archive_requires_post_and_volunteer_role(self):
        url = reverse("eksplorasi:arsip_toggle", args=[self.future_activity.pk])
        self.client.force_login(self.volunteer)
        self.assertEqual(self.client.get(url).status_code, 405)
        self.client.force_login(self.future_activity.organizer)
        self.assertEqual(self.client.post(url).status_code, 403)
        self.assertFalse(ArsipKegiatan.objects.exists())

    def test_past_activity_has_archive_action(self):
        self.client.force_login(self.volunteer)
        response = self.client.get(reverse("eksplorasi:index"))
        self.assertContains(response, reverse("eksplorasi:arsip_toggle", args=[self.past_activity.pk]))
        self.client.post(reverse("eksplorasi:arsip_toggle", args=[self.past_activity.pk]))
        self.assertTrue(ArsipKegiatan.objects.filter(
            pengguna=self.volunteer, kegiatan=self.past_activity
        ).exists())

    def test_archive_page_is_private_to_volunteer(self):
        url = reverse("eksplorasi:arsip_daftar")
        self.assertEqual(self.client.get(url).status_code, 302)
        self.client.force_login(self.future_activity.organizer)
        self.assertEqual(self.client.get(url).status_code, 403)

    def test_old_collection_page_redirects_to_archive(self):
        self.client.force_login(self.volunteer)
        response = self.client.get(reverse("eksplorasi:koleksi_daftar"))
        self.assertRedirects(response, reverse("eksplorasi:arsip_daftar"))
