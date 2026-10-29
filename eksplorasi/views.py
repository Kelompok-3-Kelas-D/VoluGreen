from django.db.models import Count, Q
from django.shortcuts import render
from django.utils import timezone

from main.models import Category
from organizer.models import Kegiatan
from volunteer.models import PendaftaranRelawan, STATUS_MENGISI_KUOTA
from volunteer.utils import inisial_pengguna

def index(request):
    now = timezone.now()
    public_activities = Kegiatan.objects.filter(
        status_publikasi=Kegiatan.StatusPublikasi.PUBLISHED,
    ).select_related("kategori", "organizer", "organizer__profile")

    query = request.GET.get("q", "").strip()
    city = request.GET.get("kota", "").strip()
    category_id = request.GET.get("kategori", "").strip()
    application_statuses = {}
    profile = None
    if request.user.is_authenticated:
        profile = getattr(request.user, "profile", None)

    activities = public_activities
    if query:
        activities = activities.filter(
            Q(nama__icontains=query)
            | Q(deskripsi__icontains=query)
            | Q(nama_lokasi__icontains=query)
            | Q(kota__icontains=query)
            | Q(organizer__profile__organization_name__icontains=query)
        )
    if city:
        activities = activities.filter(kota__iexact=city)
    if category_id.isdigit():
        activities = activities.filter(kategori_id=int(category_id))
    activity_list = list(activities.order_by("tanggal_mulai"))
    reserved_counts = dict(
        PendaftaranRelawan.objects.filter(
            kegiatan__in=activity_list,
            status__in=STATUS_MENGISI_KUOTA,
        ).values("kegiatan_id").annotate(total=Count("pk")).values_list("kegiatan_id", "total")
    )
    if request.user.is_authenticated and profile and profile.role == "volunteer":
        application_statuses = dict(
            PendaftaranRelawan.objects.filter(
                relawan=request.user, kegiatan__in=activity_list
            ).values_list("kegiatan_id", "status")
        )
    status_labels = dict(PendaftaranRelawan.Status.choices)
    for activity in activity_list:
        activity.is_past = activity.tanggal_mulai < now
        activity.available_spots = max(activity.kuota - reserved_counts.get(activity.pk, 0), 0)
        activity.application_status = application_statuses.get(activity.pk, "")
        activity.application_status_display = status_labels.get(activity.application_status, "")
    upcoming_activities = [activity for activity in activity_list if not activity.is_past]
    past_activities = [activity for activity in reversed(activity_list) if activity.is_past]

    categories = Category.objects.filter(
        is_active=True,
        organizer_activities__status_publikasi=Kegiatan.StatusPublikasi.PUBLISHED,
    ).distinct()
    cities = (
        Kegiatan.objects.filter(
            status_publikasi=Kegiatan.StatusPublikasi.PUBLISHED,
        )
        .exclude(kota="")
        .order_by("kota")
        .values_list("kota", flat=True)
        .distinct()
    )
    return render(
        request,
        "eksplorasi/index.html",
        {
            "activities": upcoming_activities,
            "past_activities": past_activities,
            "categories": categories,
            "cities": cities,
            "query": query,
            "selected_city": city,
            "selected_category": category_id,
            "application_statuses": application_statuses,
            "volunteer_initials": (
                inisial_pengguna(request.user)
                if request.user.is_authenticated and profile and profile.role == "volunteer"
                else ""
            ),
        },
    )
