from django.conf import settings
from django.db import models


# Legacy data is retained so existing saved activities can be imported into ArsipKegiatan.
class KoleksiKegiatan(models.Model):
    pengguna = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="koleksi",
    )
    nama = models.CharField(max_length=100)
    catatan = models.TextField(blank=True)
    kegiatan = models.ManyToManyField(
        "organizer.Kegiatan",
        related_name="koleksi",
        blank=True,
    )
    dibuat_pada = models.DateTimeField(auto_now_add=True)
    diperbarui_pada = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-diperbarui_pada"]
        verbose_name_plural = "koleksi kegiatan"
        constraints = [
            models.UniqueConstraint(
                fields=["pengguna", "nama"],
                name="eksplorasi_koleksi_unik_per_user",
            )
        ]

    def __str__(self):
        return f"{self.nama} ({self.pengguna})"


class ArsipKegiatan(models.Model):
    pengguna = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="arsip_kegiatan"
    )
    kegiatan = models.ForeignKey(
        "organizer.Kegiatan", on_delete=models.CASCADE, related_name="arsip_relawan"
    )
    disimpan_pada = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-disimpan_pada"]
        constraints = [
            models.UniqueConstraint(
                fields=["pengguna", "kegiatan"], name="eksplorasi_arsip_unik_per_user"
            )
        ]
