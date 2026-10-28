from django.urls import path
from django.views.generic import RedirectView

app_name = "relawan"

urlpatterns = [
    path(
        "",
        RedirectView.as_view(
            pattern_name="volunteer:halaman_dashboard_relawan",
            permanent=False,
        ),
        name="dashboard",
    ),
    path(
        "kegiatan/<int:kegiatan_id>/daftar/",
        RedirectView.as_view(
            url="/volunteer/kegiatan/%(kegiatan_id)s/daftar/",
            permanent=False,
        ),
        name="apply",
    ),
    path(
        "pendaftaran/<uuid:pendaftaran_id>/batalkan/",
        RedirectView.as_view(
            pattern_name="volunteer:halaman_dashboard_relawan",
            permanent=False,
        ),
        name="cancel",
    ),
]
