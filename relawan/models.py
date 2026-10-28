from django.conf import settings
from django.db import models


class PendaftaranKegiatan(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Menunggu konfirmasi"
        ACCEPTED = "accepted", "Diterima"
        REJECTED = "rejected", "Tidak diterima"
        CANCELLED = "cancelled", "Dibatalkan relawan"
        ATTENDED = "attended", "Hadir"
        ABSENT = "absent", "Tidak hadir"

    relawan = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="pendaftaran_kegiatan",
    )
    kegiatan = models.ForeignKey(
        "organizer.Kegiatan",
        on_delete=models.CASCADE,
        related_name="pendaftaran",
    )
    status = models.CharField(
        max_length=12,
        choices=Status.choices,
        default=Status.PENDING,
    )
    pesan = models.CharField(max_length=500, blank=True)
    dibuat_pada = models.DateTimeField(auto_now_add=True)
    diperbarui_pada = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-dibuat_pada"]
        constraints = [
            models.UniqueConstraint(
                fields=["relawan", "kegiatan"],
                name="relawan_satu_daftar_per_kegiatan",
            )
        ]
        indexes = [
            models.Index(fields=["kegiatan", "status"]),
            models.Index(fields=["relawan", "status"]),
        ]

    def __str__(self):
        return f"{self.relawan} · {self.kegiatan} · {self.get_status_display()}"

    @property
    def dapat_dibatalkan(self):
        return self.status in {self.Status.PENDING, self.Status.ACCEPTED}
