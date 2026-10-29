from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.template.context import Context
from django.test import TestCase
from django.urls import reverse

from .forms import RegistrationForm
from .models import OrganizationSubmission, Profile


User = get_user_model()


class AuthenticationFlowTests(TestCase):
    password = "AksiHijau!2026"

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Django 5.2's Context.__copy__ is incompatible with Python 3.14;
        # the test client copies rendered contexts only for inspection.
        cls._context_copy_compat = patch.object(Context, "__copy__", lambda context: context)
        cls._context_copy_compat.start()

    @classmethod
    def tearDownClass(cls):
        cls._context_copy_compat.stop()
        super().tearDownClass()

    def volunteer_payload(self):
        return {
            "role": Profile.Role.VOLUNTEER,
            "name": "Budi Hijau",
            "username": "budi@example.com",
            "phone_number": "+62 812 3456 7890",
            "city": "Depok, Jawa Barat",
            "organization_type": "",
            "password1": self.password,
            "password2": self.password,
            "terms": "on",
        }

    def test_register_page_uses_original_ui_structure(self):
        response = self.client.get(reverse("main:register"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'class="collage"')
        self.assertContains(response, 'id="reg-role"')
        self.assertContains(response, 'id="r-email"')
        self.assertContains(response, 'id="r-pass"')

    def test_home_is_landing_page_with_login_and_register_links(self):
        response = self.client.get(reverse("main:home"))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'id="f-quick"')
        self.assertNotContains(response, 'id="home-login-form"')
        self.assertNotContains(response, 'id="f-login"')
        self.assertContains(response, f'href="{reverse("main:login")}"')
        self.assertContains(response, f'href="{reverse("main:register")}"')
        self.assertContains(response, f'href="{reverse("eksplorasi:index")}"')

    def test_registration_login_link_preserves_selected_role(self):
        response = self.client.get(reverse("main:register"), {"role": "organizer"})
        self.assertContains(
            response,
            f'id="register-login-link" href="{reverse("main:login")}?role=organizer"',
        )

    def test_volunteer_home_links_to_own_dashboard_without_organizer_signup(self):
        self.client.post(reverse("main:register"), self.volunteer_payload())
        self.client.force_login(User.objects.get(username="budi@example.com"))
        response = self.client.get(reverse("main:home"))
        self.assertContains(response, f'href="{reverse("volunteer:halaman_dashboard_relawan")}"')
        self.assertNotContains(response, "Jadi penyelenggara")

    def test_staff_home_does_not_offer_profile_without_profile_record(self):
        staff = User.objects.create_user("admin@example.com", password=self.password, is_staff=True)
        self.client.force_login(staff)
        response = self.client.get(reverse("main:home"))
        self.assertContains(response, f'href="{reverse("admin_panel:dashboard")}"')
        self.assertNotContains(response, f'href="{reverse("main:profile_settings")}"')

    def test_login_page_does_not_offer_admin_role(self):
        response = self.client.get(reverse("main:login"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-role="volunteer"')
        self.assertContains(response, 'data-role="organizer"')
        self.assertNotContains(response, 'data-role="admin"')

    def test_volunteer_registration_creates_user_and_profile(self):
        response = self.client.post(
            reverse("main:register"),
            self.volunteer_payload(),
        )

        self.assertRedirects(response, f'{reverse("main:login")}?role=volunteer')
        user = User.objects.get(username="budi@example.com")
        self.assertEqual(user.email, "budi@example.com")
        self.assertEqual(user.first_name, "Budi Hijau")
        self.assertTrue(user.check_password(self.password))
        self.assertEqual(user.profile.role, Profile.Role.VOLUNTEER)
        self.assertEqual(user.profile.city, "Depok, Jawa Barat")

    def test_organizer_registration_stores_organization_data(self):
        payload = self.volunteer_payload()
        payload.update(
            {
                "role": Profile.Role.ORGANIZER,
                "name": "Bank Sampah Hijau",
                "username": "halo@hijau.id",
                "city": "Depok, Jawa Barat",
                "organization_type": Profile.OrganizationType.WASTE_BANK,
                "organization_description": "Mengelola bank sampah dan edukasi warga.",
            }
        )

        response = self.client.post(reverse("main:register"), payload)

        self.assertRedirects(response, f'{reverse("main:login")}?role=organizer')
        profile = User.objects.get(username="halo@hijau.id").profile
        self.assertEqual(profile.role, Profile.Role.ORGANIZER)
        self.assertEqual(profile.organization_name, "Bank Sampah Hijau")
        self.assertEqual(
            profile.organization_type,
            Profile.OrganizationType.WASTE_BANK,
        )
        submission = OrganizationSubmission.objects.get(contact_email="halo@hijau.id")
        self.assertEqual(submission.name, "Bank Sampah Hijau")
        self.assertEqual(submission.city, "Depok, Jawa Barat")
        self.assertEqual(submission.description, "Mengelola bank sampah dan edukasi warga.")
        self.assertEqual(submission.status, OrganizationSubmission.Status.PENDING)

    def test_duplicate_email_is_shown_as_form_error(self):
        payload = self.volunteer_payload()
        User.objects.create_user(
            username=payload["username"],
            password=self.password,
        )

        response = self.client.post(reverse("main:register"), payload)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Email ini sudah terdaftar.")
        self.assertEqual(
            User.objects.filter(username=payload["username"]).count(),
            1,
        )

    def test_database_username_collision_is_shown_as_form_error(self):
        payload = self.volunteer_payload()

        def collide_during_save(form):
            User.objects.create_user(
                username=form.cleaned_data["username"],
                password=self.password,
            )
            raise IntegrityError("UNIQUE constraint failed: auth_user.username")

        with patch.object(
            RegistrationForm,
            "save",
            autospec=True,
            side_effect=collide_during_save,
        ):
            response = self.client.post(reverse("main:register"), payload)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Email ini sudah terdaftar.")
        self.assertEqual(
            User.objects.filter(username=payload["username"]).count(),
            1,
        )

    def test_login_checks_selected_role_and_creates_session(self):
        self.client.post(reverse("main:register"), self.volunteer_payload())

        wrong_role = self.client.post(
            reverse("main:login"),
            {
                "username": "budi@example.com",
                "password": self.password,
                "role": Profile.Role.ORGANIZER,
            },
        )
        self.assertEqual(wrong_role.status_code, 200)
        self.assertContains(wrong_role, "Peran yang dipilih tidak sesuai")

        response = self.client.post(
            reverse("main:login"),
            {
                "username": "budi@example.com",
                "password": self.password,
                "role": Profile.Role.VOLUNTEER,
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("volunteer:halaman_dashboard_relawan"))
        self.assertIn("_auth_user_id", self.client.session)
        self.assertIn("last_login", response.cookies)

        profile_page = self.client.get(reverse("main:profile_settings"))
        self.assertContains(profile_page, "Budi Hijau")
        self.assertContains(profile_page, "budi@example.com")

    def test_quick_login_detects_organizer_role_automatically(self):
        payload = self.volunteer_payload()
        payload.update(
            {
                "role": Profile.Role.ORGANIZER,
                "name": "Bank Sampah Hijau",
                "username": "halo@hijau.id",
                "city": "",
                "organization_type": Profile.OrganizationType.WASTE_BANK,
            }
        )
        self.client.post(reverse("main:register"), payload)

        response = self.client.post(
            reverse("main:login"),
            {
                "username": "halo@hijau.id",
                "password": self.password,
                "role": "",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("organizer:dashboard"))
