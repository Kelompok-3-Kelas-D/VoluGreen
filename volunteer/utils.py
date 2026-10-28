# =====================================================================
# === START BAGIAN MICGUEL (MODUL 3: ALUR RELAWAN / PENDAFTARAN) ======
# =====================================================================
"""
Adapter pembacaan atribut ``Kegiatan`` untuk Modul 3 (Alur Relawan).

Model ``Kegiatan`` milik Modul 4 (``organizer.models.Kegiatan``) memakai nama
field ``nama``, ``tanggal_mulai``, ``nama_lokasi``, ``kota``, ``kategori`` (FK),
``kuota``, ``status_publikasi``, dan ``organizer``. Seluruh pembacaan atribut
tersebut dipusatkan di file ini sehingga, jika anggota lain mengganti nama
field, cukup file ini yang perlu disesuaikan (tidak menyebar ke views/template).
"""
from django.urls import reverse
from django.utils import timezone
from django.utils.text import Truncator

HARI = ("Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu")
BULAN = (
    "", "Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli",
    "Agustus", "September", "Oktober", "November", "Desember",
)

#: Field pada ``Kegiatan`` yang dipakai untuk pencarian kata kunci ``?q=``.
FIELD_PENCARIAN_KEGIATAN = ("nama", "nama_lokasi", "alamat", "kota")

#: Relasi ``Kegiatan`` yang di-``select_related`` agar tidak terjadi N+1 query.
RELASI_KEGIATAN = ("kegiatan__kategori", "kegiatan__organizer")


# ---------------------------------------------------------------------
# Format tanggal & pengguna
# ---------------------------------------------------------------------
def iso(dt):
    """ISO-8601 string atau ``None`` (aman untuk JsonResponse)."""
    return dt.isoformat() if dt else None


def format_tanggal_id(dt):
    """Contoh: ``Sabtu, 14 November 2026 · 07.00 UTC`` (mengikuti TIME_ZONE)."""
    if not dt:
        return ""
    if timezone.is_aware(dt):
        dt = timezone.localtime(dt)
    zona = dt.tzname() or ""
    return f"{HARI[dt.weekday()]}, {dt.day} {BULAN[dt.month]} {dt.year} · {dt:%H.%M} {zona}".strip()


def nama_pengguna(user):
    if user is None:
        return ""
    return (user.get_full_name() or "").strip() or user.get_username()


def inisial_pengguna(user):
    kata = nama_pengguna(user).replace("@", " ").split()
    return "".join(k[0] for k in kata[:2]).upper() or "?"


def adalah_akun_penyelenggara(user):
    """True jika user memiliki ``profile.role == 'organizer'`` (Modul 1).

    Aman dipanggil walaupun model ``Profile`` belum ada di branch ini.
    """
    profile = getattr(user, "profile", None)
    return getattr(profile, "role", None) == "organizer"


# ---------------------------------------------------------------------
# Atribut Kegiatan
# ---------------------------------------------------------------------
def judul_kegiatan(kegiatan):
    return getattr(kegiatan, "nama", None) or getattr(kegiatan, "judul", None) or str(kegiatan)


def tanggal_kegiatan(kegiatan):
    return getattr(kegiatan, "tanggal_mulai", None) or getattr(kegiatan, "tanggal_kegiatan", None)


def kategori_kegiatan(kegiatan):
    kategori = getattr(kegiatan, "kategori", None)
    if kategori is None:
        return ""
    return getattr(kategori, "nama", None) or str(kategori)


def lokasi_kegiatan(kegiatan):
    bagian = []
    for nilai in (
        getattr(kegiatan, "nama_lokasi", None) or getattr(kegiatan, "lokasi", None),
        getattr(kegiatan, "kota", None),
    ):
        if nilai and nilai not in bagian:
            bagian.append(nilai)
    return ", ".join(bagian)


def penyelenggara_id(kegiatan):
    return getattr(kegiatan, "organizer_id", None) or getattr(kegiatan, "penyelenggara_id", None)


def nama_penyelenggara(kegiatan):
    user = getattr(kegiatan, "organizer", None) or getattr(kegiatan, "penyelenggara", None)
    if user is None:
        return ""
    profile = getattr(user, "profile", None)
    return getattr(profile, "organization_name", "") or nama_pengguna(user)


def kegiatan_dipublikasikan(kegiatan):
    """Padanan ``is_active``: Modul 4 memakai ``status_publikasi == 'published'``."""
    if hasattr(kegiatan, "is_published"):
        return bool(kegiatan.is_published)
    return bool(getattr(kegiatan, "is_active", True))


def kegiatan_sudah_lewat(kegiatan):
    tanggal = tanggal_kegiatan(kegiatan)
    return tanggal is None or tanggal <= timezone.now()


def kuota_kegiatan(kegiatan):
    return getattr(kegiatan, "kuota", 0) or 0


def kuota_terisi(kegiatan):
    """Jumlah pendaftar yang masih memegang kursi (PENDING/ACCEPTED/COMPLETED)."""
    from .models import STATUS_MENGISI_KUOTA  # import lokal: hindari circular import

    return kegiatan.pendaftar_kegiatan.filter(status__in=STATUS_MENGISI_KUOTA).count()


def sisa_kuota(kegiatan, terisi=None):
    if terisi is None:
        terisi = kuota_terisi(kegiatan)
    return max(kuota_kegiatan(kegiatan) - terisi, 0)


def kegiatan_to_dict(kegiatan, terisi=None):
    """Ringkasan kegiatan yang siap diserialisasi ke JSON."""
    if terisi is None:
        terisi = kuota_terisi(kegiatan)
    tanggal = tanggal_kegiatan(kegiatan)
    deskripsi = getattr(kegiatan, "deskripsi", "") or ""
    return {
        "id": kegiatan.pk,
        "judul": judul_kegiatan(kegiatan),
        "deskripsi_singkat": Truncator(deskripsi).chars(160),
        "kategori": kategori_kegiatan(kegiatan),
        "lokasi": lokasi_kegiatan(kegiatan),
        "kota": getattr(kegiatan, "kota", "") or "",
        "tanggal": iso(tanggal),
        "tanggal_display": format_tanggal_id(tanggal),
        "sudah_lewat": kegiatan_sudah_lewat(kegiatan),
        "dipublikasikan": kegiatan_dipublikasikan(kegiatan),
        "penyelenggara": nama_penyelenggara(kegiatan),
        "kuota": kuota_kegiatan(kegiatan),
        "kuota_terisi": terisi,
        "sisa_kuota": sisa_kuota(kegiatan, terisi),
        "url_daftar": reverse("volunteer:halaman_daftar_kegiatan", args=[kegiatan.pk]),
    }
# =====================================================================
# === END BAGIAN MICGUEL (MODUL 3: ALUR RELAWAN / PENDAFTARAN) ========
# =====================================================================

