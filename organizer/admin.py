from django.contrib import admin

from .models import DampakKegiatan, Kategori, Kegiatan


@admin.register(Kategori)
class KategoriAdmin(admin.ModelAdmin):
    list_display = ("nama",)
    search_fields = ("nama",)


class DampakInline(admin.StackedInline):
    model = DampakKegiatan
    extra = 0


@admin.register(Kegiatan)
class KegiatanAdmin(admin.ModelAdmin):
    list_display = ("nama", "organizer", "kategori", "kota", "tanggal_mulai", "kuota", "status_publikasi")
    list_filter = ("status_publikasi", "kategori", "kota")
    search_fields = ("nama", "nama_lokasi", "kota")
    inlines = [DampakInline]
