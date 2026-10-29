from django.urls import path

from . import views

app_name = "eksplorasi"

urlpatterns = [
    path("", views.index, name="index"),
    path("api/kegiatan/", views.api_kegiatan, name="api_kegiatan"),
    path("koleksi/", views.koleksi_daftar, name="koleksi_daftar"),
    path("koleksi/buat/", views.koleksi_buat, name="koleksi_buat"),
    path("koleksi/<int:pk>/", views.koleksi_detail, name="koleksi_detail"),
    path("koleksi/<int:pk>/ubah/", views.koleksi_edit, name="koleksi_edit"),
    path("koleksi/<int:pk>/hapus/", views.koleksi_hapus, name="koleksi_hapus"),
    path("koleksi/<int:pk>/kegiatan/<int:kegiatan_pk>/", views.koleksi_toggle, name="koleksi_toggle"),
    path("kegiatan/<int:pk>/", views.detail_kegiatan, name="detail"),
]
