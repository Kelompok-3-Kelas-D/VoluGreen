from django.test import TestCase
from django.urls import reverse


class LegacyRelawanRouteTests(TestCase):
    def test_old_dashboard_url_redirects_to_volunteer_app(self):
        response = self.client.get(reverse("relawan:dashboard"))
        self.assertRedirects(
            response,
            reverse("volunteer:halaman_dashboard_relawan"),
            fetch_redirect_response=False,
        )
