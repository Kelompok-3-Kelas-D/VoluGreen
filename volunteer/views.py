# =====================================================================
# === START BAGIAN MICGUEL (MODUL 3: ALUR RELAWAN / PENDAFTARAN) ======
# =====================================================================
import json

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models import Count, Q, Sum
from django.db.models.functions import Coalesce
from django.http import Http404, JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.http import (
    require_GET,
    require_http_methods,
    require_POST,
)

from organizer.models import Kegiatan

from . import utils
from .decorators import relawan_login_required as login_required
from .forms import (
    PembatalanPendaftaranForm,
    PendaftaranCreateForm,
    PendaftaranUpdateForm,
    RefleksiRiwayatForm,
)
from .models import (
    PESAN_DUPLIKAT,
    STATUS_MENGISI_KUOTA,
    PendaftaranRelawan,
    StatusPendaftaran,
    alasan_tidak_bisa_mendaftar,
)

STATUS_TERLARANG_DIUBAH_RELAWAN = {
    StatusPendaftaran.ACCEPTED,
    StatusPendaftaran.REJECTED,
    StatusPendaftaran.COMPLETED,
}


# ---------------------------------------------------------------------
# Helper internal untuk parsing payload & format error JSON
# ---------------------------------------------------------------------
def _parse_payload(request):
    """Membaca body JSON (application/json) maupun FormData / request.POST."""
    content_type = (request.content_type or "").lower()
    if "application/json" in content_type:
        raw_body = request.body.decode("utf-8").strip() if request.body else ""
        if not raw_body:
            return {}, None
        try:
            parsed = json.loads(raw_body)
        except json.JSONDecodeError:
            return None, JsonResponse(
                {
                    "status": "error",
                    "message": "Format payload JSON tidak valid.",
                    "errors": {"__all__": ["Format payload JSON tidak valid."]},
                },
                status=400,
            )
        if not isinstance(parsed, dict):
            return None, JsonResponse(
                {
                    "status": "error",
                    "message": "Payload JSON harus berupa objek key-value.",
                    "errors": {"__all__": ["Payload JSON harus berupa objek key-value."]},
                },
                status=400,
            )
        return parsed, None

    if request.POST:
        return request.POST.dict(), None

    if request.body:
        try:
            parsed = json.loads(request.body.decode("utf-8"))
            if isinstance(parsed, dict):
                return parsed, None
        except (UnicodeDecodeError, json.JSONDecodeError):
            pass

    return {}, None


def _format_form_errors(form):
    """Mengubah ErrorDict Django menjadi dict sederhana {field: [pesan]} + pesan utama."""
    errors = {}
    pesan_utama = None
    for field, daftar in form.errors.get_json_data().items():
        daftar_pesan = [item.get("message", "") for item in daftar if item.get("message")]
        if daftar_pesan:
            errors[field] = daftar_pesan
            if pesan_utama is None:
                pesan_utama = daftar_pesan[0]
    return errors, pesan_utama or "Data yang dikirimkan belum valid."


def _ambil_kegiatan_atau_404(kegiatan_id, lock=False):
    """Mengambil objek Kegiatan berdasarkan PK dengan penanganan tipe PK yang aman."""
    qs = Kegiatan.objects.select_related("kategori", "organizer")
    if lock:
        qs = qs.select_for_update()
    try:
        obj = qs.filter(pk=kegiatan_id).first()
    except (ValueError, TypeError, ValidationError):
        obj = None
    if obj is None:
        raise Http404("Kegiatan tidak ditemukan.")
    return obj


def _ambil_pendaftaran_relawan_atau_404(user, pendaftaran_id, lock=False):
    """Mengambil PendaftaranRelawan milik user yang sedang login."""
    qs = PendaftaranRelawan.objects.select_related("relawan", *utils.RELASI_KEGIATAN)
    if lock:
        qs = qs.select_for_update()
    try:
        obj = qs.filter(pk=pendaftaran_id, relawan=user).first()
    except (ValueError, TypeError, ValidationError):
        obj = None
    if obj is None:
        raise Http404("Data pendaftaran tidak ditemukan.")
    return obj


def _ringkasan_status_relawan(user):
    """Menghitung agregasi jumlah pendaftaran per status dan total jam kontribusi."""
    qs = PendaftaranRelawan.objects.filter(relawan=user)
    agregasi = qs.aggregate(
        total=Count("id"),
        menunggu=Count("id", filter=Q(status=StatusPendaftaran.PENDING)),
        diterima=Count("id", filter=Q(status=StatusPendaftaran.ACCEPTED)),
        ditolak=Count("id", filter=Q(status=StatusPendaftaran.REJECTED)),
        dibatalkan=Count("id", filter=Q(status=StatusPendaftaran.CANCELLED)),
        selesai=Count("id", filter=Q(status__in=[StatusPendaftaran.COMPLETED, StatusPendaftaran.ABSENT]) | Q(hadir=True)),
        total_jam_kontribusi=Coalesce(
            Sum("jam_kontribusi", filter=Q(status=StatusPendaftaran.COMPLETED) | Q(hadir=True)),
            0,
        ),
    )
    return {
        "total": agregasi["total"] or 0,
        "menunggu": agregasi["menunggu"] or 0,
        "diterima": agregasi["diterima"] or 0,
        "ditolak": agregasi["ditolak"] or 0,
        "dibatalkan": agregasi["dibatalkan"] or 0,
        "selesai": agregasi["selesai"] or 0,
        "total_kegiatan_diikuti": agregasi["selesai"] or 0,
        "total_jam_kontribusi": agregasi["total_jam_kontribusi"] or 0,
        # Alias kode status untuk kemudahan pembacaan di front-end & test
        "PENDING": agregasi["menunggu"] or 0,
        "ACCEPTED": agregasi["diterima"] or 0,
        "REJECTED": agregasi["ditolak"] or 0,
        "CANCELLED": agregasi["dibatalkan"] or 0,
        "COMPLETED": agregasi["selesai"] or 0,
    }


# ---------------------------------------------------------------------
# Views Halaman HTML (@login_required)
# ---------------------------------------------------------------------
@login_required
@require_GET
def halaman_daftar_kegiatan(request, kegiatan_id):
    """Merender halaman formulir pendaftaran relawan (daftar_kegiatan.html)."""
    kegiatan = _ambil_kegiatan_atau_404(kegiatan_id)
    pendaftaran = (
        PendaftaranRelawan.objects.select_related("relawan", *utils.RELASI_KEGIATAN)
        .filter(relawan=request.user, kegiatan=kegiatan)
        .first()
    )
    sudah_terdaftar = bool(
        pendaftaran is not None and pendaftaran.status != StatusPendaftaran.CANCELLED
    )
    alasan_blokir = alasan_tidak_bisa_mendaftar(
        request.user,
        kegiatan,
        pendaftaran_lama=pendaftaran,
    )
    terisi = utils.kuota_terisi(kegiatan)
    context = {
        "kegiatan": kegiatan,
        "kegiatan_info": utils.kegiatan_to_dict(kegiatan, terisi=terisi),
        "sudah_terdaftar": sudah_terdaftar,
        "pendaftaran": pendaftaran,
        "bisa_mendaftar": alasan_blokir is None,
        "alasan_tidak_bisa_mendaftar": alasan_blokir,
        "nama_relawan": utils.nama_pengguna(request.user),
        "inisial_relawan": utils.inisial_pengguna(request.user),
    }
    return render(request, "volunteer/daftar_kegiatan.html", context)


@login_required
@require_GET
def halaman_dashboard_relawan(request):
    """Merender halaman gabungan Status Pendaftaran & Riwayat Partisipasi Relawan."""
    ringkasan = _ringkasan_status_relawan(request.user)
    daftar_kegiatan_tersedia = (
        Kegiatan.objects.select_related("kategori", "organizer")
        .filter(
            status_publikasi=Kegiatan.StatusPublikasi.PUBLISHED,
            tanggal_mulai__gt=timezone.now(),
        )
        .order_by("tanggal_mulai")[:6]
    )
    status_saya = dict(
        PendaftaranRelawan.objects.filter(
            relawan=request.user,
            kegiatan__in=[k.pk for k in daftar_kegiatan_tersedia],
        ).values_list("kegiatan_id", "status")
    )
    kegiatan_tersedia = []
    for k in daftar_kegiatan_tersedia:
        info = utils.kegiatan_to_dict(k)
        kode = status_saya.get(k.pk)
        info["status_saya"] = kode
        info["status_saya_label"] = StatusPendaftaran(kode).label if kode else ""
        info["sudah_terdaftar"] = kode in STATUS_MENGISI_KUOTA
        kegiatan_tersedia.append(info)
    context = {
        "ringkasan": ringkasan,
        "pilihan_status": StatusPendaftaran.choices,
        "nama_relawan": utils.nama_pengguna(request.user),
        "inisial_relawan": utils.inisial_pengguna(request.user),
        "email_relawan": request.user.email or request.user.get_username(),
        "daftar_kegiatan_tersedia": kegiatan_tersedia,
    }
    return render(request, "volunteer/dashboard_relawan.html", context)


# ---------------------------------------------------------------------
# Endpoint AJAX CRUD (@login_required)
# ---------------------------------------------------------------------
@login_required
@require_POST
def daftar_kegiatan_ajax(request, kegiatan_id):
    """CREATE — Mendaftarkan request.user sebagai relawan pada suatu kegiatan."""
    payload, error_response = _parse_payload(request)
    if error_response is not None:
        return error_response

    try:
        with transaction.atomic():
            kegiatan = _ambil_kegiatan_atau_404(kegiatan_id, lock=True)
            form = PendaftaranCreateForm(
                data=payload,
                relawan=request.user,
                kegiatan=kegiatan,
            )
            if not form.is_valid():
                errors, pesan = _format_form_errors(form)
                return JsonResponse(
                    {
                        "status": "error",
                        "message": pesan,
                        "errors": errors,
                    },
                    status=400,
                )
            pendaftaran = form.save()
    except IntegrityError:
        return JsonResponse(
            {
                "status": "error",
                "message": PESAN_DUPLIKAT,
                "errors": {"__all__": [PESAN_DUPLIKAT]},
            },
            status=400,
        )

    return JsonResponse(
        {
            "status": "success",
            "message": "Pendaftaran relawan berhasil dikirim dan sedang menunggu konfirmasi penyelenggara.",
            "data": pendaftaran.to_dict(),
        },
        status=201,
    )


@login_required
@require_GET
def lihat_daftar_status_ajax(request):
    """READ STATUS LIST — Daftar pendaftaran milik request.user dengan filter & pencarian."""
    status_filter = (request.GET.get("status") or "").strip().upper()
    kata_kunci = (request.GET.get("q") or "").strip()

    qs = (
        PendaftaranRelawan.objects.select_related("relawan", *utils.RELASI_KEGIATAN)
        .filter(relawan=request.user)
        .order_by("-waktu_daftar")
    )

    status_valid = {pilihan[0] for pilihan in StatusPendaftaran.choices}
    if status_filter and status_filter != "ALL":
        if status_filter not in status_valid:
            return JsonResponse(
                {
                    "status": "error",
                    "message": f"Filter status '{status_filter}' tidak dikenal.",
                },
                status=400,
            )
        qs = qs.filter(status=status_filter)

    if kata_kunci:
        q_filter = Q(kegiatan__kategori__name__icontains=kata_kunci)
        for nama_field in utils.FIELD_PENCARIAN_KEGIATAN:
            q_filter |= Q(**{f"kegiatan__{nama_field}__icontains": kata_kunci})
        qs = qs.filter(q_filter)

    daftar_item = [item.to_dict() for item in qs]
    ringkasan = _ringkasan_status_relawan(request.user)

    return JsonResponse(
        {
            "status": "success",
            "count": len(daftar_item),
            "summary": ringkasan,
            "ringkasan": ringkasan,
            "filters": {
                "status": status_filter or "ALL",
                "q": kata_kunci,
            },
            "data": daftar_item,
        },
        status=200,
    )


@login_required
@require_GET
def detail_status_pendaftaran_ajax(request, pendaftaran_id):
    """READ DETAIL — Mengembalikan detail satu pendaftaran milik request.user."""
    pendaftaran = _ambil_pendaftaran_relawan_atau_404(request.user, pendaftaran_id)
    return JsonResponse(
        {
            "status": "success",
            "data": pendaftaran.to_dict(),
        },
        status=200,
    )


@login_required
@require_GET
def cek_status_pada_kegiatan_ajax(request, kegiatan_id):
    """CHECK STATUS PER KEGIATAN — Mengecek apakah request.user sudah terdaftar pada kegiatan."""
    kegiatan = _ambil_kegiatan_atau_404(kegiatan_id)
    pendaftaran = (
        PendaftaranRelawan.objects.select_related("relawan", *utils.RELASI_KEGIATAN)
        .filter(relawan=request.user, kegiatan=kegiatan)
        .first()
    )
    is_registered = bool(
        pendaftaran is not None and pendaftaran.status in STATUS_MENGISI_KUOTA
    )
    alasan_blokir = alasan_tidak_bisa_mendaftar(
        request.user,
        kegiatan,
        pendaftaran_lama=pendaftaran,
    )
    return JsonResponse(
        {
            "status": "success",
            "is_registered": is_registered,
            "sudah_terdaftar": is_registered,
            "bisa_mendaftar": alasan_blokir is None,
            "alasan_tidak_bisa_mendaftar": alasan_blokir,
            "status_pendaftaran": pendaftaran.status if pendaftaran else None,
            "status_label": pendaftaran.get_status_display() if pendaftaran else None,
            "data": pendaftaran.to_dict() if pendaftaran else None,
        },
        status=200,
    )


@login_required
@require_http_methods(["POST", "PUT", "PATCH"])
def ubah_pendaftaran_ajax(request, pendaftaran_id):
    """UPDATE — Mengubah informasi pendaftaran atau menyimpan refleksi partisipasi relawan."""
    payload, error_response = _parse_payload(request)
    if error_response is not None:
        return error_response

    with transaction.atomic():
        pendaftaran = _ambil_pendaftaran_relawan_atau_404(
            request.user,
            pendaftaran_id,
            lock=True,
        )

        # Cegah relawan memalsukan status menjadi ACCEPTED, REJECTED, atau COMPLETED
        if "status" in payload:
            status_diminta = str(payload.get("status") or "").strip().upper()
            if status_diminta in STATUS_TERLARANG_DIUBAH_RELAWAN:
                return JsonResponse(
                    {
                        "status": "error",
                        "message": "Relawan tidak memiliki izin untuk mengubah status konfirmasi pendaftaran.",
                    },
                    status=403,
                )
            if status_diminta == StatusPendaftaran.CANCELLED:
                return _proses_pembatalan(pendaftaran, payload)
            if status_diminta and status_diminta != pendaftaran.status:
                return JsonResponse(
                    {
                        "status": "error",
                        "message": "Perubahan status pendaftaran tersebut tidak diizinkan.",
                    },
                    status=403,
                )

        # Cabang 1: Penyimpanan refleksi riwayat partisipasi
        hanya_refleksi = (
            "refleksi_relawan" in payload
            and not any(
                k in payload
                for k in ("motivasi", "kontak_darurat", "pengalaman_relevan", "kebutuhan_khusus")
            )
        )
        if hanya_refleksi or pendaftaran.masuk_riwayat_partisipasi:
            if "refleksi_relawan" in payload:
                if not pendaftaran.masuk_riwayat_partisipasi:
                    return JsonResponse(
                        {
                            "status": "error",
                            "message": "Refleksi hanya dapat diisi setelah kegiatan selesai diikuti.",
                        },
                        status=400,
                    )
                form_refleksi = RefleksiRiwayatForm(data=payload, instance=pendaftaran)
                if not form_refleksi.is_valid():
                    errors, pesan = _format_form_errors(form_refleksi)
                    return JsonResponse(
                        {
                            "status": "error",
                            "message": pesan,
                            "errors": errors,
                        },
                        status=400,
                    )
                pendaftaran = form_refleksi.save()
                return JsonResponse(
                    {
                        "status": "success",
                        "message": "Refleksi partisipasi berhasil disimpan.",
                        "data": pendaftaran.to_dict(),
                    },
                    status=200,
                )

        # Cabang 2: Pengubahan informasi pendaftaran (motivasi, kontak darurat, dll.)
        if not pendaftaran.bisa_diubah_informasinya:
            return JsonResponse(
                {
                    "status": "error",
                    "message": (
                        "Informasi pendaftaran sudah tidak dapat diubah karena status pendaftaran "
                        f"'{pendaftaran.get_status_display()}' atau jadwal kegiatan telah lewat."
                    ),
                },
                status=400,
            )

        data_gabungan = {
            "motivasi": payload.get("motivasi", pendaftaran.motivasi),
            "kontak_darurat": payload.get("kontak_darurat", pendaftaran.kontak_darurat),
            "pengalaman_relevan": payload.get(
                "pengalaman_relevan",
                pendaftaran.pengalaman_relevan,
            ),
            "kebutuhan_khusus": payload.get(
                "kebutuhan_khusus",
                pendaftaran.kebutuhan_khusus,
            ),
        }
        form_ubah = PendaftaranUpdateForm(data=data_gabungan, instance=pendaftaran)
        if not form_ubah.is_valid():
            errors, pesan = _format_form_errors(form_ubah)
            return JsonResponse(
                {
                    "status": "error",
                    "message": pesan,
                    "errors": errors,
                },
                status=400,
            )

        pendaftaran = form_ubah.save()

    return JsonResponse(
        {
            "status": "success",
            "message": "Informasi pendaftaran berhasil diperbarui.",
            "data": pendaftaran.to_dict(),
        },
        status=200,
    )


def _proses_pembatalan(pendaftaran, payload):
    """Helper terpusat untuk memvalidasi dan mengeksekusi pembatalan pendaftaran."""
    if not pendaftaran.bisa_dibatalkan:
        return JsonResponse(
            {
                "status": "error",
                "message": (
                    "Pendaftaran ini tidak dapat dibatalkan karena berstatus "
                    f"'{pendaftaran.get_status_display()}' atau jadwal kegiatan telah lewat."
                ),
            },
            status=400,
        )

    data_batal = {
        "alasan_pembatalan": (
            payload.get("alasan_pembatalan")
            if "alasan_pembatalan" in payload
            else payload.get("alasan", "")
        )
    }
    form_batal = PembatalanPendaftaranForm(data=data_batal)
    if not form_batal.is_valid():
        errors, pesan = _format_form_errors(form_batal)
        return JsonResponse(
            {
                "status": "error",
                "message": pesan,
                "errors": errors,
            },
            status=400,
        )

    pendaftaran.batalkan(alasan=form_batal.cleaned_data["alasan_pembatalan"])
    return JsonResponse(
        {
            "status": "success",
            "message": "Pendaftaran berhasil dibatalkan.",
            "data": pendaftaran.to_dict(),
        },
        status=200,
    )


@login_required
@require_http_methods(["POST", "PUT", "PATCH", "DELETE"])
def batalkan_pendaftaran_ajax(request, pendaftaran_id):
    """CANCEL — Membatalkan pendaftaran relawan beserta alasan pembatalannya."""
    payload, error_response = _parse_payload(request)
    if error_response is not None:
        return error_response

    with transaction.atomic():
        pendaftaran = _ambil_pendaftaran_relawan_atau_404(
            request.user,
            pendaftaran_id,
            lock=True,
        )
        return _proses_pembatalan(pendaftaran, payload)


@login_required
@require_GET
def lihat_riwayat_partisipasi_ajax(request):
    """READ HISTORY & IMPACT — Riwayat partisipasi selesai, metrik dampak, dan log batal/ditolak."""
    qs_dasar = PendaftaranRelawan.objects.select_related(
        "relawan", *utils.RELASI_KEGIATAN
    ).filter(relawan=request.user)

    qs_selesai = qs_dasar.filter(
        Q(status=StatusPendaftaran.COMPLETED) | Q(hadir=True)
    ).order_by("-waktu_selesai_partisipasi", "-waktu_daftar")

    metrik = qs_selesai.aggregate(
        total_kegiatan_diikuti=Count("id"),
        total_jam_kontribusi=Coalesce(Sum("jam_kontribusi"), 0),
    )

    qs_tidak_aktif = qs_dasar.filter(
        status__in=[StatusPendaftaran.CANCELLED, StatusPendaftaran.REJECTED, StatusPendaftaran.ABSENT]
    ).order_by("-waktu_diperbarui")

    daftar_riwayat = [item.to_dict() for item in qs_selesai]
    daftar_log = [item.to_dict() for item in qs_tidak_aktif]

    total_kegiatan = metrik["total_kegiatan_diikuti"] or 0
    total_jam = metrik["total_jam_kontribusi"] or 0

    return JsonResponse(
        {
            "status": "success",
            "metrik_dampak": {
                "total_kegiatan_diikuti": total_kegiatan,
                "total_jam_kontribusi": total_jam,
            },
            "total_kegiatan_diikuti": total_kegiatan,
            "total_jam_kontribusi": total_jam,
            "data": daftar_riwayat,
            "riwayat_partisipasi": daftar_riwayat,
            "riwayat_dibatalkan_ditolak": daftar_log,
            "log_tidak_aktif": daftar_log,
        },
        status=200,
    )
# =====================================================================
# === END BAGIAN MICGUEL (MODUL 3: ALUR RELAWAN / PENDAFTARAN) ========
# =====================================================================
