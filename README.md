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

---

## 🧩 Daftar Modul (Rencana)

- **Modul 1:** Autentikasi & Manajemen Profil
- **Modul 2:** Eksplorasi Kegiatan & Pemetaan
- **Modul 3:** Alur Relawan (Volunteer)
- **Modul 4:** Dashboard Penyelenggara (Organizer)
- **Modul 5:** Admin Panel & Integrasi Data

---

## 🌐 Public API / Mock API yang Akan Dipakai

| API | Fungsi di Aplikasi |
| --- | --- |
| 🗺️ OpenStreetMap (Leaflet.js + Nominatim API) | Menampilkan titik lokasi tiap acara di peta Beranda; mengonversi nama lokasi jadi koordinat saat acara dibuat; mendukung filter acara berdasarkan kedekatan lokasi. |
| ☀️ Open-Meteo API | Menampilkan prakiraan cuaca pada tanggal acara karena sebagian besar acara volunteer lingkungan berlangsung di luar ruangan. |
| 🗂️ JSON Server (Mock API Organisasi) | Menampilkan daftar seluruh penyelenggara terverifikasi, memuat detail informasi full profil penyelenggara, serta mendukung verifikasi penyelenggara oleh Admin. |

---

## 🎭 Peran Pengguna (User Roles)

| User | Roles |
| --- | --- |
| 🤝  Relawan (Volunteer) | Membuat akun, mencari kegiatan, melihat detail, mendaftar, membatalkan pendaftaran, melihat status, dan melihat riwayat dampak. |
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
| Rayhan | Admin Panel & Integrasi Data | Pusat verifikasi penyelenggara, moderasi lowongan/kegiatan, manajemen JSON Server (Mock API), dan integrasi Retrofit. |

---

Made with love by Kelompok 3 - Kelas D
