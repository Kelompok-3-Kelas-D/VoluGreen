# 🌱 VoluGreen

## 👥 Anggota Kelompok 3 Kelas D

| Nama | NPM |
| --- | --- |
| Aqila Zoya Yuwono | 2506620293 |
| Felisha Angeline | 2506656740 |
| Micguel Katili | 2506588065 |
| Muhammad Syamil | 2506547746 |
| Rayhan Fairuz Aqram | 2506586186 |

---

## 💡 Ide Aplikasi

### Nama Aplikasi
**VoluGreen**

### Deskripsi
VoluGreen adalah platform yang menghubungkan masyarakat dengan komunitas atau organisasi untuk mengikuti kegiatan volunteer sustainable living. Pengguna dapat mencari dan mendaftar berbagai kegiatan seperti aksi bersih lingkungan, urban farming, penanaman pohon, dan kegiatan ramah lingkungan lainnya.

Melalui VoluGreen:
🙋 *Organizer* dapat membuat dan mengelola lowongan kegiatan serta memantau dampak yang dihasilkan.
🤝 *Volunteer* dapat menemukan kegiatan, melakukan pendaftaran, dan melihat riwayat partisipasi mereka.
⚙️ Platform ini dilengkapi dengan sistem verifikasi penyelenggara dan moderasi konten oleh *admin*.

### Tujuan
- Mempermudah pengguna menemukan kegiatan lingkungan berdasarkan lokasi, kategori, dan waktu.
- Membantu organisasi mempublikasikan dan mengelola kebutuhan relawan.
- Menyediakan proses pendaftaran kegiatan yang jelas dan dapat dilacak.
- Menampilkan dampak kontribusi relawan dalam bentuk metrik sederhana.

### Target Pengguna
- Mahasiswa dan masyarakat perkotaan yang mencari kegiatan volunteer berdurasi singkat.
- Komunitas lingkungan, bank sampah, kebun komunitas, dan organisasi sosial.
- Kampus atau penyelenggara acara yang menjalankan program keberlanjutan.

---

## 🔗 Repositori Git

**Link repositori:** [github.com/Kelompok-3-Kelas-D/VoluGreen](https://github.com/Kelompok-3-Kelas-D/VoluGreen)

**Situs deployment PWS:** [rayhan-fairuz51-volugreen.pws.cs.ui.ac.id](https://rayhan-fairuz51-volugreen.pws.cs.ui.ac.id/)

---

## 🧩 Daftar Modul (Rencana)

- **Modul 1:** Autentikasi & Manajemen Profil
- **Modul 2:** Eksplorasi Kegiatan & Pemetaan
- **Modul 3:** Alur Relawan (Volunteer)
- **Modul 4:** Dashboard Penyelenggara (Organizer)
- **Modul 5:** Admin Panel & Integrasi Data

---

## Integrasi data

| API | Fungsi di Aplikasi |
| --- | --- |
| 🗺️ OpenStreetMap dan Nominatim | Peta organizer dan pencarian lokasi kegiatan yang diminta pengguna. |
| 🗃️ Database Django | Menyimpan akun, profil organisasi, kategori, draft/kegiatan terbit, pendaftaran relawan, riwayat kontribusi, moderasi, dan laporan. |

### Mock JSON API untuk antarmuka

- `GET /api/mock/activities/?q=&kota=&kategori=&limit=` mengembalikan kegiatan terbit yang akan datang beserta penyelenggara, kota, kategori, dan sisa kuota.
- `GET /api/mock/organizers/?q=&kota=&limit=` mengembalikan penyelenggara terverifikasi beserta jenis organisasi dan jumlah kegiatan mendatang.
- `GET /api/mock/community/` mengembalikan hitungan agregat relawan, penyelenggara, organisasi terverifikasi, dan kegiatan mendatang. Data relawan pribadi tidak dipublikasikan.
- API ini menyediakan kontrak JSON untuk antarmuka dan membaca rekaman Django yang sama; tidak ada data kegiatan atau organisasi contoh yang ditambahkan.

### Menjalankan panel admin lokal

1. Pasang dependensi Django dengan `python -m pip install -r requirements.txt`.
2. Siapkan database dan akun admin: `python manage.py migrate`, lalu `python manage.py createsuperuser`.
3. Jalankan situs dengan `python manage.py runserver`.
4. Buka `http://localhost:8000/` untuk situs, `/eksplorasi/` untuk mencari kegiatan, `/volunteer/` untuk dashboard relawan, `/organizer/` untuk dashboard penyelenggara, atau `/admin-panel/` untuk panel admin. Masuk memakai akun yang sesuai perannya.

Panel membaca data Django. Tidak ada perintah seed contoh yang dijalankan otomatis; data tampil setelah organisasi, kegiatan, kategori, atau laporan benar-benar dibuat.

Panel admin kustom dipisahkan sebagai Django app `admin_panel`, dengan URL, view, template, aset, tes, serta model moderasi dan laporan miliknya sendiri. Model `ActivityModeration` dan `UserReport` tetap memakai tabel database yang sama saat dipindahkan, sehingga data lama tidak perlu dibuat ulang. Panel memakai kategori dan pengajuan organisasi bersama dari `main`, serta kegiatan dari `organizer`; akses tetap khusus akun staff.

### Modul autentikasi dan penyelenggara

- Daftar dan masuk tersedia di `/register/` dan `/login/`; profil membedakan relawan dan penyelenggara.
- Pendaftaran penyelenggara otomatis membuat pengajuan berstatus menunggu di panel admin.
- Dashboard `/organizer/` memakai kategori admin yang sama untuk membuat, mengubah, menghapus draft, dan mencatat dampak kegiatan.
- Admin memverifikasi organisasi dan meninjau draft sebelum kegiatan diterbitkan. Kegiatan organizer yang telah terbit muncul di antrean kegiatan admin.
- Modul eksplorasi `/eksplorasi/` mencari kegiatan terbit berdasarkan kata kunci, kota, dan kategori. Kegiatan dengan waktu mulai yang sudah lewat tetap tampil di bagian Kegiatan sebelumnya tanpa tombol pendaftaran. Lokasi kegiatan dapat dibuka di OpenStreetMap.
- App `volunteer` menangani form pendaftaran, status, pembatalan, dan riwayat. `/volunteer/` menampilkan dashboard relawan; halaman dari Cari kegiatan memeriksa kuota dan mengirim pendaftaran ke database yang sama dengan organizer. Endpoint JSON berada di `/volunteer/api/` dan hanya dapat diakses oleh akun relawan yang sudah login.
- Organizer menerima/menolak pendaftar dari dashboard `/organizer/`, lalu menandai kehadiran setelah acara. Hasilnya langsung tercermin di status, kuota, dan riwayat relawan.
- Migrasi `volunteer.0002_import_legacy_registrations` menyalin pendaftaran lama beserta statusnya ke model baru. URL `/relawan/` tetap menjadi alias kompatibilitas ke app `volunteer`; model lama tidak dipakai lagi oleh alur aktif.

### Deployment

1. Salin `.env.example` ke `.env` untuk konfigurasi lokal. Jangan commit `.env` atau secret.
2. Di server, atur `PRODUCTION=True`, `DEBUG=False`, `DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, serta kredensial PostgreSQL `DB_*` dan `SCHEMA`.
3. Pasang dependensi, jalankan `python manage.py migrate`, lalu `python manage.py collectstatic --noinput`.
4. Jalankan `gunicorn volugreen.wsgi:application --bind 0.0.0.0:$PORT` (perintah juga tersedia di `Procfile`). Pastikan platform memberi HTTPS dan variabel lingkungan tadi.

Interface menjaga navigasi konsisten, memberi umpan balik pada tindakan dan kesalahan, mempertahankan filter, mencegah pendaftaran ganda/kuota berlebih, serta membatasi perubahan status berdasarkan peran dan waktu kegiatan. Pembatalan relawan wajib menyertakan alasan; organizer mengelola keputusan dan kehadiran.

---

## 🎭 Peran Pengguna (User Roles)

| User | Roles |
| --- | --- |
| 🤝  Relawan (Volunteer) | Membuat akun, mencari dan menyimpan kegiatan, mengirim form pendaftaran, membatalkan dengan alasan, melihat status, serta riwayat kontribusi. |
| 🙋 Penyelenggara (Organizer) | Membuat dan mengubah lowongan, menentukan kuota, meninjau pendaftar, mengonfirmasi kehadiran, dan mencatat dampak kegiatan. |
| ⚙️ Admin | Memverifikasi penyelenggara, memoderasi lowongan, mengelola kategori, dan menangani laporan pengguna. |

---

## 🧑‍💻 Pembagian Modul per Anggota

| Anggota | Modul | Tanggung Jawab Utama |
| --- | --- | --- |
| Syamil | Autentikasi & Profil | Pengelolaan login, register, otorisasi peran (*User Roles*), dan profil pengguna. |
| Felisha | Eksplorasi Kegiatan & Pemetaan | Pencarian kegiatan volunteer, filter kategori, serta integrasi peta lokasi acara (OpenStreetMap). |
| Micguel | Alur Relawan (Volunteer) | Pendaftaran kegiatan, pelacakan status pendaftaran, pembatalan, dan riwayat partisipasi relawan. |
| Zoya | Dashboard Penyelenggara (Organizer) | Pembuatan & pengelolaan lowongan acara, peninjauan pendaftar, konfirmasi kehadiran, dan pencatatan dampak kegiatan. |
| Rayhan | Admin Panel & Integrasi Data | Pusat verifikasi penyelenggara, moderasi kegiatan, pengelolaan kategori dan catatan laporan. |

---

Made with love by Kelompok 3 - Kelas D

### Status integrasi saat ini

- Direktori menampilkan kegiatan terbit dari database.
- Eksplorasi menggunakan kegiatan dan lokasi dari database; koleksi kegiatan tersimpan per akun.
- Dashboard organizer menyimpan draft dan catatan dampak ke database.
- Alur pendaftaran, pembatalan, status, dan pencatatan kehadiran relawan tersimpan di database. Pemeriksaan dokumen organisasi belum tersedia dan tidak ditampilkan sebagai fitur.
- Database lokal bersih dari rekaman seed demo. Kategori konfigurasi tetap tersimpan.
