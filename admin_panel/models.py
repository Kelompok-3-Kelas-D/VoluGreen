from django.conf import settings
from django.db import models

from main.models import Category


class ActivityModeration(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Menunggu tinjauan"
        APPROVED = "approved", "Disetujui"
        REJECTED = "rejected", "Ditolak"

    title = models.CharField(max_length=160)
    organizer_name = models.CharField(max_length=160)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="activities",
    )
    description = models.TextField(blank=True)
    event_date = models.DateField(null=True, blank=True)
    location = models.CharField(max_length=200, blank=True)
    status = models.CharField(
        max_length=12,
        choices=Status.choices,
        default=Status.PENDING,
    )
    moderator_note = models.TextField(blank=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "main_activitymoderation"
        ordering = ["status", "-created_at"]
        verbose_name = "activity moderation record"
        verbose_name_plural = "activity moderation records"

    def __str__(self):
        return self.title


class UserReport(models.Model):
    class Status(models.TextChoices):
        OPEN = "open", "Baru"
        REVIEWING = "reviewing", "Ditinjau"
        RESOLVED = "resolved", "Selesai"

    reporter = models.CharField(max_length=160)
    subject = models.CharField(max_length=200)
    details = models.TextField()
    status = models.CharField(
        max_length=12,
        choices=Status.choices,
        default=Status.OPEN,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "main_userreport"
        ordering = ["status", "-created_at"]

    def __str__(self):
        return self.subject


# ---------------------------------------------------------------------------
# REFERENSI LATIHAN LIVE CODING ADMIN PANEL
#
# Potongan di bawah sengaja berupa komentar: ini contoh jawaban latihan, bukan
# fitur aktif. Jika diminta mengerjakan salah satu soal, pindahkan potongan yang
# relevan ke lokasi yang tertulis, hapus tanda komentar (#), lalu buat dan
# jalankan migrasi jika perubahan menyentuh field/opsi model:
#   python manage.py makemigrations admin_panel
#   python manage.py migrate
# ---------------------------------------------------------------------------

# SOAL 1 — Tambahkan prioritas untuk laporan pengguna.
# Lokasi: di dalam class UserReport, setelah class Status dan sebelum field
# reporter. Tambahkan field priority setelah field status.
#
#     class Priority(models.TextChoices):
#         LOW = "low", "Rendah"
#         NORMAL = "normal", "Normal"
#         HIGH = "high", "Tinggi"
#
#     priority = models.CharField(
#         max_length=10,
#         choices=Priority.choices,
#         default=Priority.NORMAL,
#     )
#
# Catatan demo: field model saja menyimpan datanya. Agar admin dapat mengubah
# prioritas dari halaman panel, form di admin_panel/templates/admin_panel/
# dashboard.html dan pemrosesan POST di admin_panel/views.py juga perlu diubah.

# SOAL 2 — Simpan email pelapor secara opsional.
# Lokasi: di dalam class UserReport, tepat setelah field reporter.
#
#     reporter_email = models.EmailField(blank=True)
#
# Jika nilai ini harus diisi lewat panel, tambahkan input form dan validasi di
# view. EmailField memvalidasi format ketika validasi form/model dijalankan.

# SOAL 3 — Tambahkan helper untuk mengecek apakah laporan masih terbuka.
# Lokasi: di dalam class UserReport, sebelum method __str__.
# Tidak perlu migrasi database karena property bukan kolom baru.
#
#     @property
#     def is_open(self):
#         return self.status != self.Status.RESOLVED

# SOAL 4 — Urutkan laporan dari yang terbaru.
# Lokasi: ganti ordering di dalam class Meta milik UserReport.
#
#     ordering = ["-created_at"]
#
# Ini mengubah urutan default query UserReport.objects.all(). Untuk menampilkan
# urutan berbeda hanya pada satu halaman, gunakan .order_by(...) di view.

# SOAL 5 — Tambahkan status “Menunggu informasi” pada laporan.
# Lokasi: di dalam class Status milik UserReport, bersama pilihan status lain.
#
#     WAITING = "waiting", "Menunggu informasi"
#
# Jika status baru dipilih dari panel, tambahkan juga <option> pada form laporan
# di dashboard.html. Pilihan yang hanya ditambahkan di model belum otomatis
# menambahkan tombol atau opsi ke antarmuka.
