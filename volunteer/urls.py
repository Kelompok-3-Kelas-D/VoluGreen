# =====================================================================
# === START BAGIAN MICGUEL (MODUL 3: ALUR RELAWAN / PENDAFTARAN) ======
# =====================================================================
from django.urls import path

from . import views

app_name = "volunteer"

urlpatterns = [
    # --- Halaman HTML ---
    path(
        "",
        views.halaman_dashboard_relawan,
        name="halaman_dashboard_relawan",
    ),
    path(
        "dashboard/",
        views.halaman_dashboard_relawan,
        name="dashboard_relawan",
    ),
    path(
        "kegiatan/<int:kegiatan_id>/daftar/",
        views.halaman_daftar_kegiatan,
        name="halaman_daftar_kegiatan",
    ),
    # --- Endpoint AJAX CRUD ---
    path(
        "api/kegiatan/<int:kegiatan_id>/daftar/",
        views.daftar_kegiatan_ajax,
        name="daftar_kegiatan_ajax",
    ),
    path(
        "api/kegiatan/<int:kegiatan_id>/cek-status/",
        views.cek_status_pada_kegiatan_ajax,
        name="cek_status_pada_kegiatan_ajax",
    ),
    path(
        "api/pendaftaran/",
        views.lihat_daftar_status_ajax,
        name="lihat_daftar_status_ajax",
    ),
    path(
        "api/pendaftaran/<uuid:pendaftaran_id>/",
        views.detail_status_pendaftaran_ajax,
        name="detail_status_pendaftaran_ajax",
    ),
    path(
        "api/pendaftaran/<uuid:pendaftaran_id>/ubah/",
        views.ubah_pendaftaran_ajax,
        name="ubah_pendaftaran_ajax",
    ),
    path(
        "api/pendaftaran/<uuid:pendaftaran_id>/batalkan/",
        views.batalkan_pendaftaran_ajax,
        name="batalkan_pendaftaran_ajax",
    ),
    path(
        "api/riwayat/",
        views.lihat_riwayat_partisipasi_ajax,
        name="lihat_riwayat_partisipasi_ajax",
    ),
]
# =====================================================================
# === END BAGIAN MICGUEL (MODUL 3: ALUR RELAWAN / PENDAFTARAN) ========
# =====================================================================
