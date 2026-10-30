from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.utils.formats import date_format
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST
from urllib.parse import urlsplit, urlunsplit

from main.models import Category
from organizer.models import Kegiatan
from volunteer.models import PendaftaranRelawan, STATUS_MENGISI_KUOTA

from .models import ArsipKegiatan

PUBLISHED = Kegiatan.StatusPublikasi.PUBLISHED


@login_required(login_url="/login/")
def index(request):
    qs, nilai = filter(request.GET)
    qs = qs.select_related("kategori", "organizer", "organizer__profile")
    semua_kegiatan = list(qs.order_by("tanggal_mulai"))
    sekarang = timezone.now()
    kegiatan_list = [item for item in semua_kegiatan if item.tanggal_mulai >= sekarang]
    kegiatan_sebelumnya = [item for item in semua_kegiatan if item.tanggal_mulai < sekarang]
    markers = data_marker(kegiatan_list)
    saved_ids = set()
    if request.user.is_authenticated:
        saved_ids = set(ArsipKegiatan.objects.filter(
            pengguna=request.user, kegiatan__in=semua_kegiatan
        ).values_list("kegiatan_id", flat=True))
    reserved = dict(
        PendaftaranRelawan.objects.filter(kegiatan__in=kegiatan_list, status__in=STATUS_MENGISI_KUOTA)
        .values("kegiatan_id").annotate(total=Count("pk")).values_list("kegiatan_id", "total")
    ) if kegiatan_list else {}
    statuses = {}
    profile = getattr(request.user, "profile", None) if request.user.is_authenticated else None
    if profile and profile.role == "volunteer":
        statuses = dict(PendaftaranRelawan.objects.filter(relawan=request.user, kegiatan__in=kegiatan_list).values_list("kegiatan_id", "status"))
    labels = dict(PendaftaranRelawan.Status.choices)
    for item in kegiatan_list:
        item.available_spots = max(item.kuota - reserved.get(item.pk, 0), 0)
        item.is_saved = item.pk in saved_ids
        item.application_status = statuses.get(item.pk, "")
        item.application_status_display = labels.get(item.application_status, "")
    for item in kegiatan_sebelumnya:
        item.is_saved = item.pk in saved_ids
    cities = sorted({item.kota for item in Kegiatan.objects.filter(status_publikasi=PUBLISHED, tanggal_mulai__gte=timezone.now()).exclude(kota="").only("kota")})
    return render(request, "eksplorasi/index.html", {
        "activities": kegiatan_list, "past_activities": kegiatan_sebelumnya, "markers": markers,
        "tanpa_koordinat": len(kegiatan_list) - len(markers),
        "categories": Category.objects.filter(is_active=True), "cities": cities,
        "query": nilai["q"], "selected_city": nilai["kota"], "selected_category": nilai["kategori"],
        "date_from": nilai["dari"], "date_to": nilai["sampai"],
        "volunteer_initials": request.user.get_username()[:2].upper() if profile and profile.role == "volunteer" else "",
    })


def filter(params):
    """Mengembalikan (queryset kegiatan published yang sudah difilter, nilai filter)."""
    qs = Kegiatan.objects.filter(status_publikasi=PUBLISHED).select_related(
        "kategori", "organizer", "organizer__profile"
    )

    nilai = {
        key: params.get(key, "").strip()
        for key in ("q", "kategori", "kota", "dari", "sampai")
    }

    if nilai["q"]:
        qs = qs.filter(
            Q(nama__icontains=nilai["q"])
            | Q(deskripsi__icontains=nilai["q"])
            | Q(nama_lokasi__icontains=nilai["q"])
            | Q(kota__icontains=nilai["q"])
            | Q(organizer__profile__organization_name__icontains=nilai["q"])
        )
    if nilai["kategori"].isdigit():
        qs = qs.filter(kategori_id=nilai["kategori"])
    if nilai["kota"]:
        qs = qs.filter(kota__icontains=nilai["kota"])

    dari = parse_date(nilai["dari"])
    sampai = parse_date(nilai["sampai"])
    if dari:
        qs = qs.filter(tanggal_mulai__date__gte=dari)
    if sampai:
        qs = qs.filter(tanggal_mulai__date__lte=sampai)

    return qs, nilai


def data_marker(kegiatan_list):
    """Data JSON-safe untuk Leaflet. Decimal diubah ke float; yang tanpa koordinat dilewati."""
    hasil = []
    for k in kegiatan_list:
        if not k.punya_koordinat:
            continue
        hasil.append(
            {
                "id": k.pk,
                "nama": k.nama,
                "lokasi": k.nama_lokasi,
                "kategori": k.kategori.name,
                "tanggal": date_format(timezone.localtime(k.tanggal_mulai), "d M Y"),
                "lat": float(k.latitude),
                "lng": float(k.longitude),
                "url": reverse("eksplorasi:detail", args=[k.pk]),
            }
        )
    return hasil


def url_valid(request, fallback):
    tujuan = request.POST.get("next", "")
    if tujuan and url_has_allowed_host_and_scheme(
        tujuan, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
        return tujuan
    return fallback

def daftar_kegiatan(request):
    qs, nilai = filter(request.GET)
    kegiatan_list = list(qs)
    markers = data_marker(kegiatan_list)
    return render(
        request,
        "eksplorasi/daftar.html",
        {
            "kegiatan_list": kegiatan_list,
            "markers": markers,
            "tanpa_koordinat": len(kegiatan_list) - len(markers),
            "kategori_list": Category.objects.filter(is_active=True),
            "filter": nilai,
            "jumlah": len(kegiatan_list),
        },
    )


def detail_kegiatan(request, pk):
    kegiatan = get_object_or_404(
        Kegiatan.objects.select_related("kategori", "organizer"),
        pk=pk,
        status_publikasi=PUBLISHED,
    )

    peta = None
    if kegiatan.punya_koordinat:
        peta = {
            "lat": float(kegiatan.latitude),
            "lng": float(kegiatan.longitude),
            "nama": kegiatan.nama_lokasi,
        }

    pendaftaran_aktif = PendaftaranRelawan.objects.filter(
        kegiatan=kegiatan, status__in=STATUS_MENGISI_KUOTA
    ).count()
    kegiatan.available_spots = max(kegiatan.kuota - pendaftaran_aktif, 0)
    kegiatan.is_past = kegiatan.tanggal_mulai <= timezone.now()
    back_url = request.GET.get("kembali", "")
    try:
        parsed_back_url = urlsplit(back_url)
    except ValueError:
        parsed_back_url = None
    if (not parsed_back_url or parsed_back_url.path != reverse("eksplorasi:index")
            or not url_has_allowed_host_and_scheme(
                back_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()
            )):
        back_url = reverse("eksplorasi:index")
    else:
        back_url = urlunsplit((parsed_back_url.scheme, parsed_back_url.netloc,
                              parsed_back_url.path, parsed_back_url.query, ""))

    profile = getattr(request.user, "profile", None) if request.user.is_authenticated else None
    application = None
    if profile and profile.role == "volunteer":
        application = PendaftaranRelawan.objects.filter(
            relawan=request.user, kegiatan=kegiatan
        ).first()

    is_archived = bool(
        profile and profile.role == "volunteer" and ArsipKegiatan.objects.filter(
            pengguna=request.user, kegiatan=kegiatan
        ).exists()
    )

    return render(
        request,
        "eksplorasi/detail.html",
        {"kegiatan": kegiatan, "peta": peta, "is_archived": is_archived,
         "application": application, "back_url": back_url},
    )


def api_kegiatan(request):
    """JSON hasil filter (dipakai AJAX/HTMX dan marker peta di Day 3)."""
    qs, _ = filter(request.GET)
    data = data_marker(list(qs))
    return JsonResponse({"count": len(data), "results": data})


@login_required(login_url="/login/")
def arsip_daftar(request):
    profile = getattr(request.user, "profile", None)
    if profile is None or profile.role != "volunteer":
        raise PermissionDenied("Arsip kegiatan hanya tersedia untuk akun relawan.")
    archives = ArsipKegiatan.objects.filter(pengguna=request.user).select_related(
        "kegiatan", "kegiatan__kategori"
    )
    return render(request, "eksplorasi/arsip.html", {
        "archives": archives,
        "volunteer_initials": request.user.get_username()[:2].upper(),
    })


@login_required(login_url="/login/")
@require_POST
def arsip_toggle(request, kegiatan_pk):
    profile = getattr(request.user, "profile", None)
    if profile is None or profile.role != "volunteer":
        raise PermissionDenied("Arsip kegiatan hanya tersedia untuk akun relawan.")

    archived = ArsipKegiatan.objects.filter(
        pengguna=request.user, kegiatan_id=kegiatan_pk
    ).first()
    if archived:
        archived.delete()
        messages.info(request, "Kegiatan dihapus dari arsip pribadimu.")
    else:
        kegiatan = get_object_or_404(Kegiatan, pk=kegiatan_pk, status_publikasi=PUBLISHED)
        ArsipKegiatan.objects.get_or_create(pengguna=request.user, kegiatan=kegiatan)
        messages.success(request, "Kegiatan tersimpan di arsip pribadimu.")
    return redirect(url_valid(request, reverse("eksplorasi:arsip_daftar")))


@login_required(login_url="/login/")
def koleksi_legacy_redirect(request, old_path=None):
    return redirect("eksplorasi:arsip_daftar")
