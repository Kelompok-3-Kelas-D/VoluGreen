# =====================================================================
# === START BAGIAN MICGUEL (MODUL 3: ALUR RELAWAN / PENDAFTARAN) ======
# =====================================================================
"""
Membuat data demo untuk mencoba Modul 3 di browser.

    python manage.py seed_relawan

Aman dijalankan berulang kali (idempotent). Akun yang dibuat:
    relawan_demo / relawan123        -> akun relawan untuk dicoba
    penyelenggara_demo / organizer123 -> pemilik kegiatan demo
    relawan_lain / relawan123        -> pengisi kuota kegiatan "penuh"
"""
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from organizer.models import Kategori, Kegiatan
from volunteer.models import PendaftaranRelawan, StatusPendaftaran

User = get_user_model()


class Command(BaseCommand):
    help = "Membuat akun & kegiatan demo untuk mencoba Modul 3 (Alur Relawan)."

    def _user(self, username, password, first, last, email):
        user, dibuat = User.objects.get_or_create(
            username=username,
            defaults={"first_name": first, "last_name": last, "email": email},
        )
        if dibuat:
            user.set_password(password)
            user.save()
        return user

    def _kegiatan(self, organizer, kategori, nama, hari, **extra):
        data = {
            "organizer": organizer,
            "kategori": kategori,
            "deskripsi": extra.pop("deskripsi", f"Kegiatan relawan lingkungan: {nama}."),
            "tanggal_mulai": timezone.now() + timedelta(days=hari),
            "nama_lokasi": extra.pop("nama_lokasi", "Lokasi kegiatan"),
            "kota": extra.pop("kota", "Depok"),
            "kuota": extra.pop("kuota", 20),
            "status_publikasi": Kegiatan.StatusPublikasi.PUBLISHED,
        }
        data.update(extra)
        kegiatan, _ = Kegiatan.objects.get_or_create(nama=nama, organizer=organizer, defaults=data)
        return kegiatan

    def _daftar(self, relawan, kegiatan, **extra):
        data = {
            "motivasi": "Ingin berkontribusi langsung menjaga lingkungan sekitar.",
            "kontak_darurat": "+62 812 3456 7890",
        }
        data.update(extra)
        obj, _ = PendaftaranRelawan.objects.get_or_create(relawan=relawan, kegiatan=kegiatan, defaults=data)
        return obj

    @transaction.atomic
    def handle(self, *args, **options):
        relawan = self._user("relawan_demo", "relawan123", "Micguel", "Katili", "relawan@volugreen.id")
        lain = self._user("relawan_lain", "relawan123", "Budi", "Santoso", "budi@volugreen.id")
        org = self._user("penyelenggara_demo", "organizer123", "Bank Sampah", "Hijau Lestari", "halo@hijaulestari.id")

        k_pohon, _ = Kategori.objects.get_or_create(nama="Penanaman pohon")
        k_bersih, _ = Kategori.objects.get_or_create(nama="Bersih lingkungan")
        k_farm, _ = Kategori.objects.get_or_create(nama="Urban farming")
        k_sampah, _ = Kategori.objects.get_or_create(nama="Bank sampah")

        # --- Kegiatan mendatang (bisa didaftar) ---
        self._kegiatan(org, k_pohon, "Tanam 500 Mangrove Muara Angke", 7,
                       nama_lokasi="Taman Wisata Alam Mangrove Angke Kapuk", kota="Jakarta Utara", kuota=30,
                       deskripsi="Menanam bibit mangrove untuk menahan abrasi pesisir Jakarta.")
        self._kegiatan(org, k_bersih, "Aksi Bersih Sungai Ciliwung", 10,
                       nama_lokasi="Bantaran Kali Ciliwung, Condet", kota="Jakarta Timur", kuota=25,
                       deskripsi="Memungut sampah di bantaran sungai dan memilahnya bersama warga.")
        k_pending = self._kegiatan(org, k_farm, "Panen Raya Kebun Komunitas Beji", 5,
                                   nama_lokasi="Kebun Komunitas Beji", kota="Depok", kuota=15)
        k_batal = self._kegiatan(org, k_sampah, "Edukasi Pemilahan Sampah RW 05", 12,
                                 nama_lokasi="Balai Warga RW 05 Pondok Cina", kota="Depok", kuota=10)
        k_penuh = self._kegiatan(org, k_bersih, "Workshop Kompos Rumah Tangga", 4,
                                 nama_lokasi="Rumah Kompos Margonda", kota="Depok", kuota=1)

        # --- Kegiatan yang sudah lewat (untuk riwayat partisipasi) ---
        k_lalu1 = self._kegiatan(org, k_bersih, "Bersih Pantai Ancol", -20,
                                 nama_lokasi="Pantai Ancol", kota="Jakarta Utara")
        k_lalu2 = self._kegiatan(org, k_pohon, "Tanam Pohon Hutan Kota UI", -45,
                                 nama_lokasi="Hutan Kota Universitas Indonesia", kota="Depok")

        # --- Pendaftaran relawan_demo dengan berbagai status ---
        self._daftar(relawan, k_pending, kebutuhan_khusus="Vegetarian")
        batal = self._daftar(relawan, k_batal)
        if batal.status == StatusPendaftaran.PENDING:
            batal.batalkan("Bentrok dengan jadwal ujian tengah semester.")

        for keg, jam, dampak in (
            (k_lalu1, 4, "Mengumpulkan 18 kg sampah plastik dari garis pantai."),
            (k_lalu2, 5, "Menanam 26 bibit pohon trembesi dan mahoni."),
        ):
            p = self._daftar(relawan, keg)
            if p.status != StatusPendaftaran.COMPLETED:
                p.tandai_selesai(jam_kontribusi=jam, catatan_dampak=dampak)

        # --- Kuota "Workshop Kompos" diisi relawan lain sehingga penuh ---
        self._daftar(lain, k_penuh, status=StatusPendaftaran.ACCEPTED)

        self.stdout.write(self.style.SUCCESS(
            "Data demo Modul 3 siap.\n"
            "  Login relawan : relawan_demo / relawan123\n"
            "  Buka          : http://127.0.0.1:8000/volunteer/"
        ))
# =====================================================================
# === END BAGIAN MICGUEL (MODUL 3: ALUR RELAWAN / PENDAFTARAN) ========
# =====================================================================

