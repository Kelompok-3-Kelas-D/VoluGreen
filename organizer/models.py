from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone


class Kategori(models.Model):
    nama = models.CharField(max_length=100, unique=True)
    deskripsi = models.TextField(blank=True)

    class Meta:
        ordering = ["nama"]
        verbose_name_plural = "kategori"

    def __str__(self):
        return self.nama


class Kegiatan(models.Model):
    class StatusPublikasi(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"
        ARCHIVED = "archived", "Diarsipkan"

    organizer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="kegiatan_dikelola",
    )
    nama = models.CharField(max_length=200)
    deskripsi = models.TextField()
    kategori = models.ForeignKey(
        Kategori,
        on_delete=models.PROTECT,
        related_name="kegiatan",
    )
    tanggal_mulai = models.DateTimeField()

    # Lokasi 
    nama_lokasi = models.CharField(max_length=255)  # dipakai geocoding Nominatim
    alamat = models.CharField(max_length=255, blank=True)
    kota = models.CharField(max_length=100, blank=True)  # filter lokasi
    # Desimal derajat, latitude dulu baru longitude. Kosong = tidak tampil di peta.
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        validators=[MinValueValidator(-90), MaxValueValidator(90)],
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        validators=[MinValueValidator(-180), MaxValueValidator(180)],
    )

    kuota = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    status_publikasi = models.CharField(
        max_length=10,
        choices=StatusPublikasi.choices,
        default=StatusPublikasi.DRAFT,
    )

    dibuat_pada = models.DateTimeField(auto_now_add=True)
    diperbarui_pada = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["tanggal_mulai"]
        verbose_name_plural = "kegiatan"
        indexes = [
            models.Index(fields=["status_publikasi", "tanggal_mulai"]),
            models.Index(fields=["kota"]),
        ]

    def __str__(self):
        return self.nama

    #helper
    @property
    def punya_koordinat(self):
        return self.latitude is not None and self.longitude is not None

    @property
    def is_published(self):
        return self.status_publikasi == self.StatusPublikasi.PUBLISHED

    @property
    def sudah_lewat(self):
        return self.tanggal_mulai < timezone.now()

    @property
    def kuota_terisi(self):
        """Jumlah pendaftar aktif. Memakai related_name 'pendaftaran' milik modul Micguel
        (status 'dibatalkan' tidak dihitung). Bernilai 0 selama model itu belum ada."""
        pendaftaran = getattr(self, "pendaftaran", None)
        if pendaftaran is None:
            return 0
        return pendaftaran.exclude(status="dibatalkan").count()

    @property
    def sisa_kuota(self):
        return max(self.kuota - self.kuota_terisi, 0)

    def dikelola_oleh(self, user):
        return user.is_authenticated and self.organizer_id == user.pk


class DampakKegiatan(models.Model):
    """Data dampak yang dicatat organizer setelah kegiatan selesai."""

    kegiatan = models.OneToOneField(
        Kegiatan, on_delete=models.CASCADE, related_name="dampak"
    )
    sampah_terkumpul_kg = models.DecimalField(
        max_digits=8, decimal_places=2, default=0, validators=[MinValueValidator(0)]
    )
    pohon_ditanam = models.PositiveIntegerField(default=0)
    area_dibersihkan_m2 = models.PositiveIntegerField(default=0)
    catatan = models.TextField(blank=True)
    dicatat_pada = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "dampak kegiatan"
        verbose_name_plural = "dampak kegiatan"

    def __str__(self):
        return f"Dampak: {self.kegiatan}"
