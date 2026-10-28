# =====================================================================
# === START BAGIAN MICGUEL (MODUL 3: ALUR RELAWAN / PENDAFTARAN) ======
# =====================================================================
from django.contrib import admin

from .models import PendaftaranRelawan, StatusPendaftaran


@admin.register(PendaftaranRelawan)
class PendaftaranRelawanAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "relawan",
        "kegiatan",
        "status",
        "hadir",
        "jam_kontribusi",
        "waktu_daftar",
    )
    list_filter = ("status", "hadir", "waktu_daftar")
    search_fields = (
        "relawan__username",
        "relawan__email",
        "relawan__first_name",
        "relawan__last_name",
        "kegiatan__nama",
        "kegiatan__nama_lokasi",
        "kegiatan__kota",
    )
    readonly_fields = ("id", "waktu_daftar", "waktu_diperbarui")
    actions = ("terima_pendaftaran", "tolak_pendaftaran", "tandai_selesai_3_jam")

    @admin.action(description="Terima pendaftaran terpilih (ACCEPTED)")
    def terima_pendaftaran(self, request, queryset):
        queryset.update(status=StatusPendaftaran.ACCEPTED)

    @admin.action(description="Tolak pendaftaran terpilih (REJECTED)")
    def tolak_pendaftaran(self, request, queryset):
        queryset.update(status=StatusPendaftaran.REJECTED)

    @admin.action(description="Tandai selesai berpartisipasi (3 jam kontribusi)")
    def tandai_selesai_3_jam(self, request, queryset):
        for obj in queryset:
            obj.tandai_selesai(
                jam_kontribusi=obj.jam_kontribusi or 3,
                catatan_dampak=obj.catatan_dampak or "Berpartisipasi penuh hingga kegiatan selesai.",
            )
# =====================================================================
# === END BAGIAN MICGUEL (MODUL 3: ALUR RELAWAN / PENDAFTARAN) ========
# =====================================================================
