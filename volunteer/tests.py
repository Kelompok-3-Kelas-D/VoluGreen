# =====================================================================
# === START BAGIAN MICGUEL (MODUL 3: ALUR RELAWAN / PENDAFTARAN) ======
# =====================================================================
import json
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from organizer.models import Kategori, Kegiatan

from .models import PendaftaranRelawan, StatusPendaftaran

User = get_user_model()


class ModulRelawanTestCase(TestCase):
    """Unit test lengkap untuk Modul 3: Alur Relawan (Volunteer)."""

    def setUp(self):
        self.organizer = User.objects.create_user(
            username="organizer1",
            email="org@volugreen.id",
            password="password123",
            first_name="Bank Sampah",
            last_name="Hijau",
        )
        self.relawan1 = User.objects.create_user(
            username="micguel",
            email="micguel@volugreen.id",
            password="password123",
            first_name="Micguel",
            last_name="Katili",
        )
        self.relawan2 = User.objects.create_user(
            username="relawan_kedua",
            email="relawan2@volugreen.id",
            password="password123",
            first_name="Budi",
            last_name="Santoso",
        )
        self.kategori = Kategori.objects.create(
            nama="Penanaman Pohon",
            deskripsi="Restorasi ekosistem pesisir dan hutan kota.",
        )
        self.kegiatan = self._buat_kegiatan(
            nama="Tanam 500 Mangrove Muara Angke",
            kota="Jakarta Utara",
            kuota=5,
        )

    def _buat_kegiatan(self, **overrides):
        data = {
            "organizer": self.organizer,
            "nama": "Aksi Bersih Sungai Ciliwung",
            "deskripsi": "Kegiatan bersih sungai bersama warga dan relawan.",
            "kategori": self.kategori,
            "tanggal_mulai": timezone.now() + timedelta(days=5),
            "nama_lokasi": "Taman Ekowisata Muara Angke",
            "kota": "Depok",
            "kuota": 10,
            "status_publikasi": Kegiatan.StatusPublikasi.PUBLISHED,
        }
        data.update(overrides)
        return Kegiatan.objects.create(**data)

    def _post_json(self, url, payload):
        return self.client.post(
            url,
            data=json.dumps(payload),
            content_type="application/json",
        )

    # ------------------------------------------------------------------
    # 1. CREATE: Pendaftaran Kegiatan Berhasil (201 Created)
    # ------------------------------------------------------------------
    def test_daftar_kegiatan_berhasil_201_created(self):
        self.client.login(username="micguel", password="password123")
        url = reverse("volunteer:daftar_kegiatan_ajax", args=[self.kegiatan.pk])
        payload = {
            "motivasi": "Saya ingin ikut menjaga ekosistem mangrove pesisir Jakarta.",
            "kontak_darurat": "+62 812 3456 7890",
            "pengalaman_relevan": "Pernah ikut aksi tanam pohon di kampus.",
            "kebutuhan_khusus": "Tidak ada",
        }
        response = self._post_json(url, payload)
        self.assertEqual(response.status_code, 201)

        body = response.json()
        self.assertEqual(body["status"], "success")
        self.assertEqual(body["data"]["status"], StatusPendaftaran.PENDING)
        self.assertEqual(body["data"]["kegiatan"]["sisa_kuota"], 4)
        self.assertEqual(PendaftaranRelawan.objects.count(), 1)
        self.assertEqual(self.kegiatan.sisa_kuota, 4)

    # ------------------------------------------------------------------
    # 2. ANTI-DUPLIKASI: Pencegahan Pendaftaran Berulang (400 & tetap 1 record)
    # ------------------------------------------------------------------
    def test_cegah_pendaftaran_berulang_pada_kegiatan_yang_sama(self):
        self.client.login(username="micguel", password="password123")
        url = reverse("volunteer:daftar_kegiatan_ajax", args=[self.kegiatan.pk])
        payload = {
            "motivasi": "Ingin berkontribusi nyata pada penanaman mangrove.",
            "kontak_darurat": "081234567890",
        }

        # Pendaftaran pertama berhasil (201)
        res1 = self._post_json(url, payload)
        self.assertEqual(res1.status_code, 201)
        self.assertEqual(PendaftaranRelawan.objects.count(), 1)

        # Pendaftaran kedua oleh relawan yang sama pada kegiatan yang sama ditolak (400)
        res2 = self._post_json(url, payload)
        self.assertEqual(res2.status_code, 400)
        self.assertEqual(res2.json()["status"], "error")
        self.assertEqual(
            PendaftaranRelawan.objects.filter(
                relawan=self.relawan1,
                kegiatan=self.kegiatan,
            ).count(),
            1,
        )

        # Validasi level model clean() dan DB UniqueConstraint juga menolak duplikasi
        duplikat = PendaftaranRelawan(
            relawan=self.relawan1,
            kegiatan=self.kegiatan,
            motivasi="Mencoba duplikasi langsung ke model.",
            kontak_darurat="081234567890",
        )
        with self.assertRaises(ValidationError):
            duplikat.full_clean()
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                duplikat.save()

    # ------------------------------------------------------------------
    # 3. VALIDASI KUOTA & JADWAL: Penolakan jika Kuota Penuh / Jadwal Lewat
    # ------------------------------------------------------------------
    def test_tolak_pendaftaran_jika_kuota_penuh_atau_jadwal_lewat(self):
        # Kasus A: Kuota hanya 1 dan sudah diisi relawan2
        kegiatan_kuota_1 = self._buat_kegiatan(nama="Workshop Kompos", kuota=1)
        PendaftaranRelawan.objects.create(
            relawan=self.relawan2,
            kegiatan=kegiatan_kuota_1,
            motivasi="Belajar mengolah sampah organik rumah tangga.",
            kontak_darurat="081299998888",
        )

        self.client.login(username="micguel", password="password123")
        url_penuh = reverse("volunteer:daftar_kegiatan_ajax", args=[kegiatan_kuota_1.pk])
        res_penuh = self._post_json(
            url_penuh,
            {
                "motivasi": "Saya ingin ikut belajar kompos bersama komunitas.",
                "kontak_darurat": "081234567890",
            },
        )
        self.assertEqual(res_penuh.status_code, 400)
        self.assertIn("penuh", res_penuh.json()["message"].lower())

        # Kasus B: Jadwal kegiatan sudah lewat
        kegiatan_lampau = self._buat_kegiatan(
            nama="Aksi Bersih Pantai Lampau",
            tanggal_mulai=timezone.now() - timedelta(days=2),
        )
        url_lampau = reverse("volunteer:daftar_kegiatan_ajax", args=[kegiatan_lampau.pk])
        res_lampau = self._post_json(
            url_lampau,
            {
                "motivasi": "Saya ingin mendaftar pada kegiatan yang sudah lewat.",
                "kontak_darurat": "081234567890",
            },
        )
        self.assertEqual(res_lampau.status_code, 400)
        self.assertIn("lewat", res_lampau.json()["message"].lower())

    # ------------------------------------------------------------------
    # 4. UPDATE & KEAMANAN STATUS: Ubah Informasi (200) & Cegah Palsukan Status (403)
    # ------------------------------------------------------------------
    def test_ubah_pendaftaran_berhasil_dan_tolak_pemalsuan_status_403(self):
        pendaftaran = PendaftaranRelawan.objects.create(
            relawan=self.relawan1,
            kegiatan=self.kegiatan,
            motivasi="Motivasi awal sebelum diperbarui oleh relawan.",
            kontak_darurat="081234567890",
        )
        self.client.login(username="micguel", password="password123")
        url_ubah = reverse("volunteer:ubah_pendaftaran_ajax", args=[pendaftaran.id])

        # Pengubahan informasi valid saat PENDING -> 200 OK
        res_ok = self._post_json(
            url_ubah,
            {
                "motivasi": "Motivasi baru yang lebih lengkap dan siap turun ke lapangan.",
                "kontak_darurat": "+62 811 2233 4455",
                "kebutuhan_khusus": "Vegetarian",
                "pengalaman_relevan": "Koordinator relawan kampus 2025",
            },
        )
        self.assertEqual(res_ok.status_code, 200)
        pendaftaran.refresh_from_db()
        self.assertEqual(pendaftaran.kebutuhan_khusus, "Vegetarian")
        self.assertEqual(pendaftaran.kontak_darurat, "+62 811 2233 4455")

        # Percobaan relawan memalsukan status sendiri menjadi ACCEPTED -> 403 Forbidden
        res_forbidden = self._post_json(
            url_ubah,
            {
                "status": "ACCEPTED",
                "motivasi": "Mencoba mengubah status sendiri menjadi diterima.",
                "kontak_darurat": "+62 811 2233 4455",
            },
        )
        self.assertEqual(res_forbidden.status_code, 403)
        pendaftaran.refresh_from_db()
        self.assertEqual(pendaftaran.status, StatusPendaftaran.PENDING)

    # ------------------------------------------------------------------
    # 5. CANCEL: Pembatalan Pendaftaran Mengubah Status ke CANCELLED
    # ------------------------------------------------------------------
    def test_batalkan_pendaftaran_mencatat_alasan_dan_waktu(self):
        pendaftaran = PendaftaranRelawan.objects.create(
            relawan=self.relawan1,
            kegiatan=self.kegiatan,
            status=StatusPendaftaran.ACCEPTED,
            motivasi="Siap mengikuti kegiatan penanaman pohon.",
            kontak_darurat="081234567890",
        )
        self.assertEqual(self.kegiatan.sisa_kuota, 4)

        self.client.login(username="micguel", password="password123")
        url_batal = reverse("volunteer:batalkan_pendaftaran_ajax", args=[pendaftaran.id])

        # Alasan terlalu pendek ditolak (400)
        res_pendek = self._post_json(url_batal, {"alasan_pembatalan": "Ada"})
        self.assertEqual(res_pendek.status_code, 400)

        # Alasan valid mengubah status menjadi CANCELLED & mengembalikan kuota
        res_batal = self._post_json(
            url_batal,
            {"alasan_pembatalan": "Ada jadwal ujian tengah semester mendadak di kampus."},
        )
        self.assertEqual(res_batal.status_code, 200)

        pendaftaran.refresh_from_db()
        self.assertEqual(pendaftaran.status, StatusPendaftaran.CANCELLED)
        self.assertEqual(
            pendaftaran.alasan_pembatalan,
            "Ada jadwal ujian tengah semester mendadak di kampus.",
        )
        self.assertIsNotNone(pendaftaran.waktu_pembatalan)
        self.assertEqual(self.kegiatan.sisa_kuota, 5)

        # Jika mendaftar ulang setelah CANCELLED, mengaktifkan record yang sama (tetap 1 baris di DB)
        url_daftar = reverse("volunteer:daftar_kegiatan_ajax", args=[self.kegiatan.pk])
        res_reapply = self._post_json(
            url_daftar,
            {
                "motivasi": "Jadwal ujian sudah diundur, saya siap hadir kembali.",
                "kontak_darurat": "081234567890",
            },
        )
        self.assertEqual(res_reapply.status_code, 201)
        self.assertEqual(PendaftaranRelawan.objects.count(), 1)
        pendaftaran.refresh_from_db()
        self.assertEqual(pendaftaran.status, StatusPendaftaran.PENDING)

    # ------------------------------------------------------------------
    # 6. RIWAYAT & METRIK DAMPAK: Akurasi Perhitungan Kegiatan & Jam Kontribusi
    # ------------------------------------------------------------------
    def test_riwayat_partisipasi_dan_akurasi_metrik_dampak(self):
        keg_1 = self._buat_kegiatan(nama="Aksi Bersih Pantai Ancol", kota="Jakarta Utara")
        keg_2 = self._buat_kegiatan(nama="Kebun Komunitas Beji", kota="Depok")
        keg_3 = self._buat_kegiatan(nama="Edukasi Bank Sampah", kota="Bogor")

        p1 = PendaftaranRelawan.objects.create(
            relawan=self.relawan1,
            kegiatan=keg_1,
            motivasi="Ikut membersihkan area pesisir pantai.",
            kontak_darurat="081234567890",
        )
        p1.tandai_selesai(jam_kontribusi=4, catatan_dampak="Mengumpulkan 15 kg sampah plastik")

        p2 = PendaftaranRelawan.objects.create(
            relawan=self.relawan1,
            kegiatan=keg_2,
            motivasi="Membantu penataan bedeng sayur organik.",
            kontak_darurat="081234567890",
        )
        p2.tandai_selesai(jam_kontribusi=5, catatan_dampak="Menanam 30 bibit cabai dan tomat")

        # Pendaftaran ke-3 dibatalkan (tidak boleh dihitung ke jam kontribusi selesai)
        p3 = PendaftaranRelawan.objects.create(
            relawan=self.relawan1,
            kegiatan=keg_3,
            motivasi="Ingin membantu edukasi warga.",
            kontak_darurat="081234567890",
        )
        p3.batalkan(alasan="Sedang sakit demam sehingga tidak bisa hadir.")

        self.client.login(username="micguel", password="password123")

        # Simpan refleksi relawan pada p1
        url_ubah_p1 = reverse("volunteer:ubah_pendaftaran_ajax", args=[p1.id])
        res_refleksi = self._post_json(
            url_ubah_p1,
            {"refleksi_relawan": "Pengalaman luar biasa bersama relawan lintas kampus!"},
        )
        self.assertEqual(res_refleksi.status_code, 200)

        # Cek endpoint riwayat partisipasi
        url_riwayat = reverse("volunteer:lihat_riwayat_partisipasi_ajax")
        res_riwayat = self.client.get(url_riwayat)
        self.assertEqual(res_riwayat.status_code, 200)

        data = res_riwayat.json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["total_kegiatan_diikuti"], 2)
        self.assertEqual(data["total_jam_kontribusi"], 9)
        self.assertEqual(data["metrik_dampak"]["total_kegiatan_diikuti"], 2)
        self.assertEqual(data["metrik_dampak"]["total_jam_kontribusi"], 9)
        self.assertEqual(len(data["data"]), 2)
        self.assertEqual(len(data["riwayat_dibatalkan_ditolak"]), 1)

    # ------------------------------------------------------------------
    # 7. FILTER STATUS, CEK STATUS PER KEGIATAN, & HALAMAN HTML
    # ------------------------------------------------------------------
    def test_filter_daftar_status_cek_status_dan_halaman_html(self):
        PendaftaranRelawan.objects.create(
            relawan=self.relawan1,
            kegiatan=self.kegiatan,
            status=StatusPendaftaran.ACCEPTED,
            motivasi="Siap mengikuti penanaman mangrove.",
            kontak_darurat="081234567890",
        )
        self.client.login(username="micguel", password="password123")

        # Cek status per kegiatan
        url_cek = reverse("volunteer:cek_status_pada_kegiatan_ajax", args=[self.kegiatan.pk])
        res_cek = self.client.get(url_cek)
        self.assertEqual(res_cek.status_code, 200)
        self.assertTrue(res_cek.json()["is_registered"])

        # Filter daftar status berdasarkan status & kata kunci
        url_list = reverse("volunteer:lihat_daftar_status_ajax")
        res_list = self.client.get(url_list, {"status": "ACCEPTED", "q": "Mangrove"})
        self.assertEqual(res_list.status_code, 200)
        self.assertEqual(res_list.json()["count"], 1)

        # Render halaman HTML daftar kegiatan & dashboard relawan
        res_page_daftar = self.client.get(
            reverse("volunteer:halaman_daftar_kegiatan", args=[self.kegiatan.pk])
        )
        self.assertEqual(res_page_daftar.status_code, 200)
        self.assertTrue(res_page_daftar.context["sudah_terdaftar"])

        res_page_dash = self.client.get(reverse("volunteer:halaman_dashboard_relawan"))
        self.assertEqual(res_page_dash.status_code, 200)

    # ------------------------------------------------------------------
    # 8. AUTENTIKASI: halaman diarahkan ke login, API mengembalikan 401
    # ------------------------------------------------------------------
    def test_belum_login_diarahkan_ke_login_dan_api_401(self):
        res_page = self.client.get(reverse("volunteer:halaman_dashboard_relawan"))
        self.assertEqual(res_page.status_code, 302)
        self.assertIn(reverse("volunteer:masuk"), res_page["Location"])

        res_login_page = self.client.get(reverse("volunteer:masuk"))
        self.assertEqual(res_login_page.status_code, 200)

        res_api = self.client.get(reverse("volunteer:lihat_daftar_status_ajax"))
        self.assertEqual(res_api.status_code, 401)

        res_login = self.client.post(
            reverse("volunteer:masuk"),
            {"username": "micguel", "password": "password123"},
        )
        self.assertRedirects(res_login, reverse("volunteer:halaman_dashboard_relawan"))

    # ------------------------------------------------------------------
    # 9. DASHBOARD: hanya kegiatan mendatang & penanda status milik relawan
    # ------------------------------------------------------------------
    def test_dashboard_lowongan_hanya_kegiatan_mendatang(self):
        self._buat_kegiatan(nama="Kegiatan Sudah Lewat", tanggal_mulai=timezone.now() - timedelta(days=1))
        PendaftaranRelawan.objects.create(
            relawan=self.relawan1,
            kegiatan=self.kegiatan,
            motivasi="Siap menanam mangrove bersama komunitas.",
            kontak_darurat="081234567890",
        )
        self.client.login(username="micguel", password="password123")
        res = self.client.get(reverse("volunteer:halaman_dashboard_relawan"))
        judul = [k["judul"] for k in res.context["daftar_kegiatan_tersedia"]]
        self.assertIn(self.kegiatan.nama, judul)
        self.assertNotIn("Kegiatan Sudah Lewat", judul)
        info = next(k for k in res.context["daftar_kegiatan_tersedia"] if k["id"] == self.kegiatan.pk)
        self.assertTrue(info["sudah_terdaftar"])

    # ------------------------------------------------------------------
    # 10. DATA DEMO: perintah seed_relawan idempotent
    # ------------------------------------------------------------------
    def test_seed_relawan_idempotent(self):
        from django.core.management import call_command
        from io import StringIO

        call_command("seed_relawan", stdout=StringIO())
        jumlah = PendaftaranRelawan.objects.count()
        call_command("seed_relawan", stdout=StringIO())
        self.assertEqual(PendaftaranRelawan.objects.count(), jumlah)

        demo = User.objects.get(username="relawan_demo")
        self.assertTrue(demo.check_password("relawan123"))
        selesai = PendaftaranRelawan.objects.filter(relawan=demo, status=StatusPendaftaran.COMPLETED)
        self.assertEqual(selesai.count(), 2)
        self.assertTrue(
            PendaftaranRelawan.objects.filter(relawan=demo, status=StatusPendaftaran.CANCELLED).exists()
        )
# =====================================================================
# === END BAGIAN MICGUEL (MODUL 3: ALUR RELAWAN / PENDAFTARAN) ========
# =====================================================================
