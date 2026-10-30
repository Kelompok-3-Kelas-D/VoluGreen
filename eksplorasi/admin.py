from django.contrib import admin

from .models import ArsipKegiatan


@admin.register(ArsipKegiatan)
class ArsipKegiatanAdmin(admin.ModelAdmin):
    list_display = ("pengguna", "kegiatan", "disimpan_pada")
    list_filter = ("disimpan_pada",)
    search_fields = ("pengguna__username", "pengguna__email", "kegiatan__nama")
