# =====================================================================
# === START BAGIAN MICGUEL (MODUL 3: ALUR RELAWAN / PENDAFTARAN) ======
# =====================================================================
"""
Model Modul 3 — Alur Relawan (Volunteer).

Catatan integrasi:
    Model ``Kegiatan`` TIDAK dibuat ulang di sini. Model tersebut sudah dibuat
    oleh Modul 4 (Organizer) di ``organizer.models.Kegiatan`` dan dipakai
    langsung sebagai target ``ForeignKey``. Pembacaan atributnya (nama,
    tanggal_mulai, lokasi, kategori, kuota, status_publikasi) dipusatkan di
    ``volunteer/utils.py``.

Aturan anti-duplikasi:
    Satu relawan hanya memiliki SATU record per kegiatan (UniqueConstraint
    ``unique_relawan_per_kegiatan``). Jika relawan pernah membatalkan
    (CANCELLED) lalu ingin mendaftar lagi, record yang sama diaktifkan kembali
    menjadi PENDING (bila kuota & jadwal masih memungkinkan) sehingga
    constraint tidak pernah dilanggar. Pendaftaran PENDING/ACCEPTED/COMPLETED
    tidak bisa didaftarkan ulang, dan pendaftaran REJECTED tidak dapat
    diajukan ulang.
"""
import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from organizer.models import Kegiatan  # Model Kegiatan milik Modul 4 (Organizer)

from . import utils

PESAN_DUPLIKAT = "Satu relawan tidak dapat mendaftar berulang kali pada kegiatan yang sama."


class StatusPendaftaran(models.TextChoices):
    PENDING = "PENDING", "Menunggu Konfirmasi"
    ACCEPTED = "ACCEPTED", "Diterima"
    REJECTED = "REJECTED", "Ditolak"
    CANCELLED = "CANCELLED", "Dibatalkan"
    COMPLETED = "COMPLETED", "Selesai Berpartisipasi"


#: Status yang masih memegang kursi kuota dan dianggap "sudah terdaftar".
STATUS_MENGISI_KUOTA = (
    StatusPendaftaran.PENDING,
    StatusPendaftaran.ACCEPTED,
    StatusPendaftaran.COMPLETED,
)
#: Status yang masih boleh diubah informasinya / dibatalkan oleh relawan.
STATUS_BISA_DIUBAH = (StatusPendaftaran.PENDING, StatusPendaftaran.ACCEPTED)


class PendaftaranRelawan(models.Model):
    StatusPendaftaran = StatusPendaftaran  # alias: PendaftaranRelawan.StatusPendaftaran.PENDING

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # --- Relasi -------------------------------------------------------
    relawan = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="pendaftaran_relawan",
    )
    kegiatan = models.ForeignKey(
        Kegiatan,
        on_delete=models.CASCADE,
        related_name="pendaftar_kegiatan",
    )

    status = models.CharField(
        max_length=10,
        choices=StatusPendaftaran.choices,
        default=StatusPendaftaran.PENDING,
        db_index=True,
    )

    # --- Informasi pendaftaran relawan -----------------------------------
    motivasi = models.TextField()
    kontak_darurat = models.CharField(max_length=30)
    pengalaman_relevan = models.TextField(blank=True, default="")
    kebutuhan_khusus = models.CharField(max_length=255, blank=True, default="")

    # --- Pembatalan ----------------------------------------------------
    alasan_pembatalan = models.TextField(blank=True, default="")
    waktu_pembatalan = models.DateTimeField(null=True, blank=True)

    # --- Riwayat partisipasi & metrik dampak ------------------------------
    hadir = models.BooleanField(default=False)
    jam_kontribusi = models.PositiveIntegerField(default=0)
    catatan_dampak = models.TextField(blank=True, default="")
    refleksi_relawan = models.TextField(blank=True, default="")
    waktu_selesai_partisipasi = models.DateTimeField(null=True, blank=True)

    # --- Timestamp -----------------------------------------------------
    waktu_daftar = models.DateTimeField(auto_now_add=True)
    waktu_diperbarui = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-waktu_daftar"]
        verbose_name = "pendaftaran relawan"
        verbose_name_plural = "pendaftaran relawan"
        constraints = [
            models.UniqueConstraint(
                fields=["relawan", "kegiatan"],
                name="unique_relawan_per_kegiatan",
            )
        ]
        indexes = [
            models.Index(fields=["relawan", "status"], name="volunteer_rel_status_idx"),
        ]

    def __str__(self):
        return f"{self.relawan} → {utils.judul_kegiatan(self.kegiatan)} ({self.get_status_display()})"

    # ------------------------------------------------------------------
    # Validasi
    # ------------------------------------------------------------------
    def clean(self):
        super().clean()
        if self.relawan_id and self.kegiatan_id:
            duplikat = (
                type(self)
                .objects.filter(relawan_id=self.relawan_id, kegiatan_id=self.kegiatan_id)
                .exclude(pk=self.pk)
                .exists()
            )
            if duplikat:
                raise ValidationError(PESAN_DUPLIKAT, code="duplikat")

    # ------------------------------------------------------------------
    # Properti
    # ------------------------------------------------------------------
    @property
    def jadwal_belum_lewat(self):
        return not utils.kegiatan_sudah_lewat(self.kegiatan)

    @property
    def bisa_diubah_informasinya(self):
        return self.status in STATUS_BISA_DIUBAH and self.jadwal_belum_lewat

    @property
    def bisa_dibatalkan(self):
        return self.status in STATUS_BISA_DIUBAH and self.jadwal_belum_lewat

    @property
    def masuk_riwayat_partisipasi(self):
        return self.status == StatusPendaftaran.COMPLETED or self.hadir

    # ------------------------------------------------------------------
    # Helper aksi
    # ------------------------------------------------------------------
    def batalkan(self, alasan=""):
        """Membatalkan pendaftaran (dipanggil setelah ``bisa_dibatalkan`` dicek)."""
        self.status = StatusPendaftaran.CANCELLED
        self.alasan_pembatalan = (alasan or "").strip()
        self.waktu_pembatalan = timezone.now()
        self.save()

    def tandai_selesai(self, jam_kontribusi=0, catatan_dampak=""):
        """Helper untuk Modul 4 (Organizer) saat mengonfirmasi kehadiran relawan."""
        try:
            jam = int(jam_kontribusi)
        except (TypeError, ValueError):
            raise ValidationError({"jam_kontribusi": "Jam kontribusi harus berupa bilangan bulat."})
        if jam < 0:
            raise ValidationError({"jam_kontribusi": "Jam kontribusi tidak boleh negatif."})
        self.status = StatusPendaftaran.COMPLETED
        self.hadir = True
        self.jam_kontribusi = jam
        self.catatan_dampak = (catatan_dampak or "").strip()
        self.waktu_selesai_partisipasi = timezone.now()
        self.save()

    def siapkan_daftar_ulang(self):
        """Mengaktifkan kembali record CANCELLED menjadi PENDING (belum disimpan)."""
        self.status = StatusPendaftaran.PENDING
        self.alasan_pembatalan = ""
        self.waktu_pembatalan = None
        self.hadir = False
        self.jam_kontribusi = 0
        self.catatan_dampak = ""
        self.refleksi_relawan = ""
        self.waktu_selesai_partisipasi = None

    # ------------------------------------------------------------------
    # Serialisasi
    # ------------------------------------------------------------------
    def to_dict(self):
        # ``kuota_terisi_anotasi`` diisi oleh queryset di views (hindari N+1 query).
        terisi = getattr(self, "kuota_terisi_anotasi", None)
        dibatalkan = self.status == StatusPendaftaran.CANCELLED
        return {
            "id": str(self.id),
            "relawan": {
                "id": self.relawan_id,
                "username": self.relawan.get_username(),
                "nama": utils.nama_pengguna(self.relawan),
            },
            "kegiatan": utils.kegiatan_to_dict(self.kegiatan, terisi=terisi),
            "status": self.status,
            "status_label": self.get_status_display(),
            "motivasi": self.motivasi,
            "kontak_darurat": self.kontak_darurat,
            "pengalaman_relevan": self.pengalaman_relevan,
            "kebutuhan_khusus": self.kebutuhan_khusus,
            "bisa_diubah": self.bisa_diubah_informasinya,
            "bisa_dibatalkan": self.bisa_dibatalkan,
            "bisa_isi_refleksi": self.masuk_riwayat_partisipasi,
            "masuk_riwayat_partisipasi": self.masuk_riwayat_partisipasi,
            "pembatalan": {
                "dibatalkan": dibatalkan,
                "alasan": self.alasan_pembatalan,
                "waktu": utils.iso(self.waktu_pembatalan),
                "waktu_display": utils.format_tanggal_id(self.waktu_pembatalan),
            },
            "riwayat_partisipasi": {
                "hadir": self.hadir,
                "jam_kontribusi": self.jam_kontribusi,
                "catatan_dampak": self.catatan_dampak,
                "refleksi_relawan": self.refleksi_relawan,
                "waktu_selesai": utils.iso(self.waktu_selesai_partisipasi),
                "waktu_selesai_display": utils.format_tanggal_id(self.waktu_selesai_partisipasi),
            },
            "waktu_daftar": utils.iso(self.waktu_daftar),
            "waktu_daftar_display": utils.format_tanggal_id(self.waktu_daftar),
            "waktu_diperbarui": utils.iso(self.waktu_diperbarui),
        }


# ----------------------------------------------------------------------
# Jembatan properti pada model Kegiatan (tanpa mengubah organizer/models.py)
# ----------------------------------------------------------------------
Kegiatan.jumlah_terdaftar_aktif = property(utils.kuota_terisi)
Kegiatan.kuota_terisi = property(utils.kuota_terisi)
if not hasattr(Kegiatan, "judul"):
    Kegiatan.judul = property(utils.judul_kegiatan)
if not hasattr(Kegiatan, "tanggal_kegiatan"):
    Kegiatan.tanggal_kegiatan = property(utils.tanggal_kegiatan)
if not hasattr(Kegiatan, "lokasi"):
    Kegiatan.lokasi = property(utils.lokasi_kegiatan)
if not hasattr(Kegiatan, "penyelenggara"):
    Kegiatan.penyelenggara = property(lambda self: getattr(self, "organizer", None))
if not hasattr(Kegiatan, "is_active"):
    Kegiatan.is_active = property(utils.kegiatan_dipublikasikan)


_BELUM_DICARI = object()


def alasan_tidak_bisa_mendaftar(relawan, kegiatan, pendaftaran_lama=_BELUM_DICARI):
    """Mengembalikan pesan alasan jika ``relawan`` tidak bisa mendaftar, atau ``None``.

    Dipakai bersama oleh form, halaman HTML, dan endpoint cek status agar
    aturan kelayakan pendaftaran hanya ditulis di satu tempat.
    """
    if pendaftaran_lama is _BELUM_DICARI:
        pendaftaran_lama = PendaftaranRelawan.objects.filter(relawan=relawan, kegiatan=kegiatan).first()

    # (a) Anti-duplikasi
    if pendaftaran_lama is not None:
        if pendaftaran_lama.status == StatusPendaftaran.REJECTED:
            return "Pendaftaranmu pada kegiatan ini telah ditolak penyelenggara sehingga tidak dapat diajukan ulang."
        if pendaftaran_lama.status != StatusPendaftaran.CANCELLED:
            return (
                f"Kamu sudah terdaftar pada kegiatan ini (status: {pendaftaran_lama.get_status_display()}). "
                f"{PESAN_DUPLIKAT}"
            )

    # Peran pengguna
    if utils.penyelenggara_id(kegiatan) == relawan.pk:
        return "Penyelenggara tidak dapat mendaftar sebagai relawan pada kegiatannya sendiri."
    if utils.adalah_akun_penyelenggara(relawan):
        return "Akun penyelenggara tidak dapat mendaftar sebagai relawan."

    # (b) Kegiatan aktif & jadwal belum lewat
    if not utils.kegiatan_dipublikasikan(kegiatan):
        return "Kegiatan ini sedang tidak membuka pendaftaran relawan."
    if utils.kegiatan_sudah_lewat(kegiatan):
        return "Jadwal kegiatan sudah lewat sehingga pendaftaran ditutup."

    # (c) Kuota
    if utils.sisa_kuota(kegiatan) <= 0:
        return "Kuota relawan untuk kegiatan ini sudah penuh."
    return None
# =====================================================================
# === END BAGIAN MICGUEL (MODUL 3: ALUR RELAWAN / PENDAFTARAN) ========
# =====================================================================
