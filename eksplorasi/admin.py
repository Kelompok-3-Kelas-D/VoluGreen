from django.contrib import admin

from .models import KoleksiKegiatan


@admin.register(KoleksiKegiatan)
class KoleksiKegiatanAdmin(admin.ModelAdmin):
    list_display = ("nama", "pengguna", "jumlah_kegiatan", "diperbarui_pada")
    list_filter = ("diperbarui_pada",)
    search_fields = ("nama", "pengguna__username", "pengguna__email")
    filter_horizontal = ("kegiatan",)

    @admin.display(description="Jumlah kegiatan")
    def jumlah_kegiatan(self, obj):
        return obj.kegiatan.count()
