from django.urls import path

from . import views

app_name = "eksplorasi"

urlpatterns = [
    path("", views.index, name="index"),
    path("api/kegiatan/", views.api_kegiatan, name="api_kegiatan"),
    path("arsip/", views.arsip_daftar, name="arsip_daftar"),
    path("arsip/<int:kegiatan_pk>/", views.arsip_toggle, name="arsip_toggle"),
    path("koleksi/", views.koleksi_legacy_redirect, name="koleksi_daftar"),
    path("koleksi/<path:old_path>", views.koleksi_legacy_redirect, name="koleksi_legacy"),
    path("kegiatan/<int:pk>/", views.detail_kegiatan, name="detail"),
]
