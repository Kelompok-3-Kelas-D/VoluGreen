from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from django.urls import reverse
from django.utils import timezone

from main.models import Category, OrganizationSubmission
from .models import ActivityModeration, UserReport
from organizer.models import Kegiatan


class AdminPanelTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.staff = User.objects.create_user(username="rayhan-admin", password="safe-test-password", is_staff=True)
        self.url = reverse("admin_panel:dashboard")

    def test_panel_requires_staff_login(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin/login/", response["Location"])

    def test_staff_can_create_update_and_delete_category(self):
        self.client.force_login(self.staff)
        response = self.client.post(self.url, {"action": "save_category", "return_page": "categories",
                                               "name": "Urban farming", "description": "Kebun kota"})
        self.assertEqual(response["Location"], f"{self.url}#categories")
        category = Category.objects.get(name="Urban farming")
        self.client.post(self.url, {"action": "save_category", "category_id": category.pk,
                                    "name": "Pertanian kota", "description": "Kebun warga", "is_active": "on"})
        category.refresh_from_db()
        self.assertEqual(category.name, "Pertanian kota")
        self.assertTrue(category.is_active)
        self.client.post(self.url, {"action": "delete_category", "category_id": category.pk})
        self.assertFalse(Category.objects.filter(pk=category.pk).exists())

    def test_staff_can_verify_organization(self):
        self.client.force_login(self.staff)
        organization = OrganizationSubmission.objects.create(name="Komunitas Hijau")
        self.client.post(self.url, {"action": "approve_organization", "organization_id": organization.pk})
        organization.refresh_from_db()
        self.assertEqual(organization.status, OrganizationSubmission.Status.VERIFIED)
        self.assertEqual(organization.verified_by, self.staff.username)

    def test_staff_can_publish_organizer_draft_from_panel(self):
        self.client.force_login(self.staff)
        organizer = get_user_model().objects.create_user(username="demo-organizer")
        organizer.email = "organizer@example.test"
        organizer.save(update_fields=["email"])
        OrganizationSubmission.objects.create(
            name="Organizer test", contact_email=organizer.email,
            status=OrganizationSubmission.Status.VERIFIED,
        )
        category = Category.objects.create(name="Tanam pohon")
        activity = Kegiatan.objects.create(
            organizer=organizer, nama="Tanam bersama", deskripsi="Aksi warga",
            kategori=category, tanggal_mulai=timezone.now(),
            nama_lokasi="Depok", kuota=10,
        )
        self.client.post(self.url, {
            "action": "approve_activity", "activity_id": activity.pk,
            "activity_source": "organizer", "return_page": "activities",
        })
        activity.refresh_from_db()
        self.assertEqual(activity.status_publikasi, Kegiatan.StatusPublikasi.PUBLISHED)

    def test_unverified_organizer_activity_cannot_be_published(self):
        self.client.force_login(self.staff)
        organizer = get_user_model().objects.create_user(
            username="pending-organizer", email="pending@example.test"
        )
        category = Category.objects.create(name="Bersih lingkungan")
        activity = Kegiatan.objects.create(
            organizer=organizer, nama="Aksi bersih", deskripsi="Aksi warga",
            kategori=category, tanggal_mulai=timezone.now(), nama_lokasi="Depok", kuota=10,
        )
        self.client.post(self.url, {
            "action": "approve_activity", "activity_id": activity.pk,
            "activity_source": "organizer", "return_page": "activities",
        })
        activity.refresh_from_db()
        self.assertEqual(activity.status_publikasi, Kegiatan.StatusPublikasi.DRAFT)

    def test_panel_renders_organization(self):
        OrganizationSubmission.objects.create(
            name="Komunitas Hijau Depok", contact_email="halo@hijaudepok.example"
        )
        request = RequestFactory().get(self.url)
        request.user = self.staff
        from .views import dashboard
        response = dashboard(request)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Komunitas Hijau Depok", response.content)
        self.assertIn(b"halo@hijaudepok.example", response.content)

    def test_staff_can_moderate_activity_and_report(self):
        self.client.force_login(self.staff)
        activity = ActivityModeration.objects.create(title="Bersih sungai", organizer_name="Komunitas Hijau")
        report = UserReport.objects.create(reporter="Nadia", subject="Konten perlu ditinjau", details="Detail laporan")
        self.client.post(self.url, {"action": "reject_activity", "activity_id": activity.pk,
                                    "moderator_note": "Informasi lokasi perlu dilengkapi."})
        self.client.post(self.url, {"action": "update_report", "report_id": report.pk, "status": "resolved"})
        activity.refresh_from_db()
        report.refresh_from_db()
        self.assertEqual(activity.status, ActivityModeration.Status.REJECTED)
        self.assertEqual(activity.reviewed_by, self.staff)
        self.assertEqual(report.status, UserReport.Status.RESOLVED)
