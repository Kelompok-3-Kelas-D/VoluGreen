from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.utils.formats import date_format
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from main.models import Category
from organizer.models import Kegiatan
from volunteer.models import PendaftaranRelawan, STATUS_MENGISI_KUOTA

from .forms import KoleksiForm
from .models import KoleksiKegiatan

PUBLISHED = Kegiatan.StatusPublikasi.PUBLISHED


def index(request):
    qs, nilai = filter(request.GET)
    qs = qs.select_related("kategori", "organizer", "organizer__profile")
    semua_kegiatan = list(qs.order_by("tanggal_mulai"))
    sekarang = timezone.now()
    kegiatan_list = [item for item in semua_kegiatan if item.tanggal_mulai >= sekarang]
    kegiatan_sebelumnya = [item for item in semua_kegiatan if item.tanggal_mulai < sekarang]
    markers = data_marker(kegiatan_list)
    saved_ids = set()
    saved_collections = {}
    collection_list = []
    if request.user.is_authenticated:
        collection_list = list(request.user.koleksi.all())
        saved_rows = KoleksiKegiatan.objects.filter(
            pengguna=request.user, kegiatan__in=kegiatan_list
        ).values_list("kegiatan__pk", "pk")
        for activity_id, collection_id in saved_rows:
            saved_ids.add(activity_id)
            saved_collections.setdefault(activity_id, set()).add(collection_id)
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
        item.saved_collection_ids = saved_collections.get(item.pk, set())
        item.application_status = statuses.get(item.pk, "")
        item.application_status_display = labels.get(item.application_status, "")
    cities = sorted({item.kota for item in Kegiatan.objects.filter(status_publikasi=PUBLISHED, tanggal_mulai__gte=timezone.now()).exclude(kota="").only("kota")})
    return render(request, "eksplorasi/index.html", {
        "activities": kegiatan_list, "past_activities": kegiatan_sebelumnya, "markers": markers,
        "tanpa_koordinat": len(kegiatan_list) - len(markers),
        "categories": Category.objects.filter(is_active=True), "cities": cities,
        "query": nilai["q"], "selected_city": nilai["kota"], "selected_category": nilai["kategori"],
        "date_from": nilai["dari"], "date_to": nilai["sampai"],
        "collection_list": collection_list,
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

    koleksi_list = []
    if request.user.is_authenticated:
        tersimpan = set(
            KoleksiKegiatan.objects.filter(
                pengguna=request.user, kegiatan=kegiatan
            ).values_list("pk", flat=True)
        )
        koleksi_list = list(request.user.koleksi.all())
        for k in koleksi_list:
            k.ada = k.pk in tersimpan

    return render(
        request,
        "eksplorasi/detail.html",
        {"kegiatan": kegiatan, "peta": peta, "koleksi_list": koleksi_list},
    )


def api_kegiatan(request):
    """JSON hasil filter (dipakai AJAX/HTMX dan marker peta di Day 3)."""
    qs, _ = filter(request.GET)
    data = data_marker(list(qs))
    return JsonResponse({"count": len(data), "results": data})


@login_required
def koleksi_daftar(request):
    koleksi_list = request.user.koleksi.annotate(jumlah=Count("kegiatan"))
    return render(request, "eksplorasi/koleksi_daftar.html", {"koleksi_list": koleksi_list})


@login_required
def koleksi_buat(request):
    form = KoleksiForm(request.POST or None, user=request.user)
    if request.method == "POST" and form.is_valid():
        koleksi = form.save(commit=False)
        koleksi.pengguna = request.user
        koleksi.save()
        messages.success(request, f"Koleksi “{koleksi.nama}” berhasil dibuat.")
        return redirect("eksplorasi:koleksi_detail", pk=koleksi.pk)
    return render(
        request,
        "eksplorasi/koleksi_form.html",
        {"form": form, "judul": "Buat koleksi baru", "tombol": "Buat koleksi"},
    )


@login_required
def koleksi_detail(request, pk):
    koleksi = get_object_or_404(KoleksiKegiatan, pk=pk, pengguna=request.user)
    kegiatan_list = koleksi.kegiatan.select_related("kategori")
    return render(
        request,
        "eksplorasi/koleksi_detail.html",
        {"koleksi": koleksi, "kegiatan_list": kegiatan_list},
    )


@login_required
def koleksi_edit(request, pk):
    koleksi = get_object_or_404(KoleksiKegiatan, pk=pk, pengguna=request.user)
    form = KoleksiForm(request.POST or None, instance=koleksi, user=request.user)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Koleksi berhasil diperbarui.")
        return redirect("eksplorasi:koleksi_detail", pk=koleksi.pk)
    return render(
        request,
        "eksplorasi/koleksi_form.html",
        {"form": form, "judul": "Ubah koleksi", "tombol": "Simpan perubahan"},
    )


@login_required
def koleksi_hapus(request, pk):
    koleksi = get_object_or_404(KoleksiKegiatan, pk=pk, pengguna=request.user)
    if request.method == "POST":
        nama = koleksi.nama
        koleksi.delete()
        messages.success(request, f"Koleksi “{nama}” dihapus.")
        return redirect("eksplorasi:koleksi_daftar")
    return render(request, "eksplorasi/koleksi_hapus.html", {"koleksi": koleksi})


@login_required
@require_POST
def koleksi_toggle(request, pk, kegiatan_pk):
    """Tambah kegiatan ke koleksi, atau keluarkan kalau sudah ada."""
    koleksi = get_object_or_404(KoleksiKegiatan, pk=pk, pengguna=request.user)

    if koleksi.kegiatan.filter(pk=kegiatan_pk).exists():
        koleksi.kegiatan.remove(kegiatan_pk)
        messages.info(request, f"Kegiatan dikeluarkan dari “{koleksi.nama}”.")
    else:
        kegiatan = get_object_or_404(Kegiatan, pk=kegiatan_pk, status_publikasi=PUBLISHED)
        koleksi.kegiatan.add(kegiatan)
        messages.success(request, f"Kegiatan ditambahkan ke “{koleksi.nama}”.")

    koleksi.save(update_fields=["diperbarui_pada"])
    return redirect(url_valid(request, reverse("eksplorasi:koleksi_detail", args=[pk])))
