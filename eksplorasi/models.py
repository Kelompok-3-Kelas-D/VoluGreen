from django.conf import settings
from django.db import models


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