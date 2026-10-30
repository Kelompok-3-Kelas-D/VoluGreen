from datetime import timedelta
from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.template.context import Context
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from main.models import Category, Profile
from volunteer.models import PendaftaranRelawan
from .models import DampakKegiatan, Kegiatan


class KegiatanModelTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user("org1", password="x")
        self.kategori = Category.objects.create(name="Bersih Lingkungan")

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


class OrganizerDashboardIntegrationTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._context_copy_compat = patch.object(Context, "__copy__", lambda context: context)
        cls._context_copy_compat.start()

    @classmethod
    def tearDownClass(cls):
        cls._context_copy_compat.stop()
        super().tearDownClass()

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="organizer@example.test", email="organizer@example.test", password="safe-password"
        )
        Profile.objects.create(
            user=self.user, role=Profile.Role.ORGANIZER, phone_number="081234567890",
            organization_name="Komunitas Tumbuh", organization_type=Profile.OrganizationType.COMMUNITY_GARDEN,
        )
        self.category = Category.objects.create(name="Urban farming")
        self.url = reverse("organizer:dashboard")
        self.client.force_login(self.user)

    def test_activity_page_only_shows_create_form_and_shared_categories(self):
        Kegiatan.objects.create(
            organizer=self.user, nama="Kegiatan lama", deskripsi="Aksi warga",
            kategori=self.category, tanggal_mulai=timezone.now() + timedelta(days=1),
            nama_lokasi="Depok", kuota=10,
        )
        response = self.client.get(reverse("organizer:activities"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Buat kegiatan")
        self.assertContains(response, "Urban farming")
        self.assertNotContains(response, "Kegiatan lama")
        self.assertNotContains(response, 'id="dampak"')

    def test_summary_groups_all_owned_activities_by_status(self):
        for name, status in [
            ("Menunggu aksi", Kegiatan.StatusPublikasi.DRAFT),
            ("Aksi terbit", Kegiatan.StatusPublikasi.PUBLISHED),
            ("Aksi arsip", Kegiatan.StatusPublikasi.ARCHIVED),
        ]:
            Kegiatan.objects.create(
                organizer=self.user, nama=name, deskripsi="Aksi warga",
                kategori=self.category, tanggal_mulai=timezone.now() + timedelta(days=1),
                nama_lokasi="Depok", kuota=10, status_publikasi=status,
            )
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Menunggu aksi")
        self.assertContains(response, "Aksi terbit")
        self.assertContains(response, "Aksi arsip")
        self.assertEqual([a["nama"] for a in response.context["pending_activities"]], ["Menunggu aksi"])
        self.assertEqual([a["nama"] for a in response.context["published_activities"]], ["Aksi terbit"])
        self.assertEqual([a["nama"] for a in response.context["archived_activities"]], ["Aksi arsip"])
        self.assertContains(response, "Menu profil penyelenggara")

    def test_activity_form_offers_default_environment_categories(self):
        response = self.client.get(reverse("organizer:activities"))
        self.assertContains(response, "Pengelolaan Sampah")
        self.assertContains(response, "Penanaman Mangrove")
        self.assertContains(response, "Pertanian Perkotaan")

    def test_profile_settings_keeps_organizer_navigation_and_avatar_menu(self):
        response = self.client.get(reverse("main:profile_settings"))
        self.assertContains(response, "Navigasi penyelenggara")
        self.assertContains(response, "Menu profil penyelenggara")
        self.assertContains(response, "Set Password")

    def test_organizer_can_save_activity_as_admin_review_draft(self):
        event_time = timezone.localtime(timezone.now() + timedelta(days=3)).strftime("%Y-%m-%dT%H:%M")
        response = self.client.post(self.url, {
            "action": "save_activity", "nama": "Kebun Akhir Pekan",
            "deskripsi": "Merawat kebun komunitas.", "kategori": self.category.pk,
            "tanggal_mulai": event_time, "nama_lokasi": "Kebun UI", "alamat": "Depok",
            "kota": "Depok", "latitude": "", "longitude": "", "kuota": 15,
        })
        self.assertRedirects(response, f'{self.url}#menunggu', fetch_redirect_response=False)
        event = Kegiatan.objects.get(nama="Kebun Akhir Pekan")
        self.assertEqual(event.organizer, self.user)
        self.assertEqual(event.status_publikasi, Kegiatan.StatusPublikasi.DRAFT)
        self.assertContains(self.client.get(self.url), "Kebun Akhir Pekan")

    def test_organizer_can_record_impact_after_published_event(self):
        event = Kegiatan.objects.create(
            organizer=self.user, nama="Bersih lingkungan", deskripsi="Aksi warga",
            kategori=self.category, tanggal_mulai=timezone.now() - timedelta(days=1),
            nama_lokasi="Depok", kuota=10,
            status_publikasi=Kegiatan.StatusPublikasi.PUBLISHED,
        )
        impact_url = reverse("organizer:impact_detail", args=[event.pk])
        response = self.client.post(impact_url, {
            "sampah_terkumpul_kg": "12.50", "pohon_ditanam": "4",
            "area_dibersihkan_m2": "80", "catatan": "Warga ikut berpartisipasi.",
        })
        self.assertRedirects(response, impact_url, fetch_redirect_response=False)
        self.assertEqual(event.dampak.sampah_terkumpul_kg, Decimal("12.50"))
        self.assertContains(self.client.get(self.url), impact_url)

    def test_invalid_impact_stays_on_report_form(self):
        event = Kegiatan.objects.create(
            organizer=self.user, nama="Bersih lingkungan", deskripsi="Aksi warga",
            kategori=self.category, tanggal_mulai=timezone.now() - timedelta(days=1),
            nama_lokasi="Depok", kuota=10,
            status_publikasi=Kegiatan.StatusPublikasi.PUBLISHED,
        )
        response = self.client.post(reverse("organizer:impact_detail", args=[event.pk]), {
            "sampah_terkumpul_kg": "-1", "pohon_ditanam": "0",
            "area_dibersihkan_m2": "0", "catatan": "",
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Laporan dampak")
        self.assertContains(response, "Sampah terkumpul")
        self.assertFalse(DampakKegiatan.objects.filter(kegiatan=event).exists())

    def test_impact_report_is_independent_and_limited_to_own_activity(self):
        first = Kegiatan.objects.create(
            organizer=self.user, nama="Aksi satu", deskripsi="Aksi warga",
            kategori=self.category, tanggal_mulai=timezone.now() - timedelta(days=1),
            nama_lokasi="Depok", kuota=10, status_publikasi=Kegiatan.StatusPublikasi.PUBLISHED,
        )
        second = Kegiatan.objects.create(
            organizer=self.user, nama="Aksi dua", deskripsi="Aksi warga",
            kategori=self.category, tanggal_mulai=timezone.now() - timedelta(days=1),
            nama_lokasi="Depok", kuota=10, status_publikasi=Kegiatan.StatusPublikasi.PUBLISHED,
        )
        other_user = get_user_model().objects.create_user("other-organizer", password="safe-password")
        other = Kegiatan.objects.create(
            organizer=other_user, nama="Aksi orang lain", deskripsi="Aksi warga",
            kategori=self.category, tanggal_mulai=timezone.now() - timedelta(days=1),
            nama_lokasi="Depok", kuota=10, status_publikasi=Kegiatan.StatusPublikasi.PUBLISHED,
        )
        data = {"sampah_terkumpul_kg": "5", "pohon_ditanam": "1", "area_dibersihkan_m2": "10", "catatan": "Selesai"}
        self.client.post(reverse("organizer:impact_detail", args=[first.pk]), data)
        self.assertTrue(DampakKegiatan.objects.filter(kegiatan=first).exists())
        self.assertFalse(DampakKegiatan.objects.filter(kegiatan=second).exists())
        self.assertEqual(self.client.get(reverse("organizer:impact_detail", args=[other.pk])).status_code, 404)
        self.assertEqual(self.client.post(reverse("organizer:impact_detail", args=[other.pk]), data).status_code, 404)

    def test_organizer_can_accept_and_reject_volunteer_application(self):
        volunteer = get_user_model().objects.create_user(
            username="relawan@example.test", password="safe-password",
        )
        Profile.objects.create(
            user=volunteer, role=Profile.Role.VOLUNTEER, phone_number="081234567891",
        )
        event = Kegiatan.objects.create(
            organizer=self.user, nama="Aksi kebun", deskripsi="Merawat kebun",
            kategori=self.category, tanggal_mulai=timezone.now() + timedelta(days=1),
            nama_lokasi="Depok", kuota=10,
            status_publikasi=Kegiatan.StatusPublikasi.PUBLISHED,
        )
        application = PendaftaranRelawan.objects.create(
            relawan=volunteer, kegiatan=event, motivasi="Ingin membantu",
            kontak_darurat="081234567891",
        )
        url = self.url

        accepted = self.client.post(url, {
            "action": "update_application", "application_id": application.pk,
            "status": PendaftaranRelawan.Status.ACCEPTED, "pesan": "Sampai jumpa!",
        })
        self.assertRedirects(accepted, f"{url}#kegiatan-{event.pk}", fetch_redirect_response=False)
        application.refresh_from_db()
        self.assertEqual(application.status, PendaftaranRelawan.Status.ACCEPTED)
        self.assertEqual(application.pesan, "Sampai jumpa!")

        rejected = self.client.post(url, {
            "action": "update_application", "application_id": application.pk,
            "status": PendaftaranRelawan.Status.REJECTED, "pesan": "Maaf, kuota berubah.",
        })
        self.assertRedirects(rejected, f"{url}#kegiatan-{event.pk}", fetch_redirect_response=False)
        application.refresh_from_db()
        self.assertEqual(application.status, PendaftaranRelawan.Status.REJECTED)
        self.assertEqual(application.pesan, "Maaf, kuota berubah.")

    def test_organizer_can_mark_accepted_volunteer_absent_after_start(self):
        volunteer = get_user_model().objects.create_user(
            username="relawan@example.test", password="safe-password",
        )
        event = Kegiatan.objects.create(
            organizer=self.user, nama="Aksi kebun", deskripsi="Merawat kebun",
            kategori=self.category, tanggal_mulai=timezone.now() - timedelta(days=1),
            nama_lokasi="Depok", kuota=10,
            status_publikasi=Kegiatan.StatusPublikasi.PUBLISHED,
        )
        application = PendaftaranRelawan.objects.create(
            relawan=volunteer, kegiatan=event, motivasi="Ingin membantu",
            kontak_darurat="081234567891",
            status=PendaftaranRelawan.Status.ACCEPTED,
        )
        url = self.url

        response = self.client.post(url, {
            "action": "update_application", "application_id": application.pk,
            "status": PendaftaranRelawan.Status.ABSENT,
        })
        self.assertRedirects(response, f"{url}#kegiatan-{event.pk}", fetch_redirect_response=False)
        application.refresh_from_db()
        self.assertEqual(application.status, PendaftaranRelawan.Status.ABSENT)
