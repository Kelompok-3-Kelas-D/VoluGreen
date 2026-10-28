from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_GET

from main.models import OrganizationSubmission, Profile
from organizer.models import Kegiatan


@require_GET
def activities(request):
    """Read-only prototype API backed by real, published Django records."""
    now = timezone.now()
    items = Kegiatan.objects.filter(
        status_publikasi=Kegiatan.StatusPublikasi.PUBLISHED,
        tanggal_mulai__gte=now,
    ).select_related("kategori", "organizer", "organizer__profile").annotate(
        active_applications=Count(
            "pendaftaran",
            filter=Q(pendaftaran__status__in=["pending", "accepted"]),
            distinct=True,
        )
    )

    query = request.GET.get("q", "").strip()
    city = request.GET.get("kota", "").strip()
    category_id = request.GET.get("kategori", "").strip()
    if query:
        items = items.filter(
            Q(nama__icontains=query)
            | Q(deskripsi__icontains=query)
            | Q(nama_lokasi__icontains=query)
            | Q(kota__icontains=query)
            | Q(organizer__profile__organization_name__icontains=query)
        )
    if city:
        items = items.filter(kota__iexact=city)
    if category_id.isdigit():
        items = items.filter(kategori_id=int(category_id))

    total = items.count()
    try:
        limit = min(max(int(request.GET.get("limit", 50)), 1), 100)
    except ValueError:
        limit = 50

    results = []
    for activity in items.order_by("tanggal_mulai")[:limit]:
        profile = getattr(activity.organizer, "profile", None)
        organizer_name = (
            profile.organization_name
            if profile and profile.organization_name
            else activity.organizer.get_username()
        )
        results.append({
            "id": activity.pk,
            "name": activity.nama,
            "description": activity.deskripsi,
            "category": activity.kategori.name,
            "starts_at": activity.tanggal_mulai.isoformat(),
            "location": {
                "name": activity.nama_lokasi,
                "city": activity.kota,
                "latitude": str(activity.latitude) if activity.latitude is not None else None,
                "longitude": str(activity.longitude) if activity.longitude is not None else None,
            },
            "organizer": {
                "id": activity.organizer_id,
                "name": organizer_name,
                "city": profile.city if profile else "",
            },
            "capacity": activity.kuota,
            "available_spots": max(activity.kuota - activity.active_applications, 0),
        })

    return JsonResponse({
        "data": results,
        "meta": {"total": total, "limit": limit, "generated_at": now.isoformat()},
    })


@require_GET
def organizers(request):
    """List verified organizations already recorded in the application."""
    query = request.GET.get("q", "").strip()
    city = request.GET.get("kota", "").strip()
    records = OrganizationSubmission.objects.filter(
        status=OrganizationSubmission.Status.VERIFIED
    )
    if query:
        records = records.filter(
            Q(name__icontains=query)
            | Q(type__icontains=query)
            | Q(description__icontains=query)
            | Q(city__icontains=query)
        )
    if city:
        records = records.filter(city__icontains=city)

    now = timezone.now()
    User = get_user_model()
    email_counts = dict(
        User.objects.filter(email__in=records.values_list("contact_email", flat=True))
        .annotate(
            published_activity_count=Count(
                "kegiatan_dikelola",
                filter=Q(
                    kegiatan_dikelola__status_publikasi=Kegiatan.StatusPublikasi.PUBLISHED,
                    kegiatan_dikelola__tanggal_mulai__gte=now,
                ),
                distinct=True,
            )
        )
        .values_list("email", "published_activity_count")
    )
    try:
        limit = min(max(int(request.GET.get("limit", 50)), 1), 100)
    except ValueError:
        limit = 50

    grouped = {}
    for record in records.order_by("name"):
        key = (record.name.strip().casefold(), record.type.strip().casefold())
        candidate = {
            "id": record.pk,
            "name": record.name,
            "type": record.type,
            "city": record.city,
            "description": record.description,
            "website": record.website,
            "published_activities": email_counts.get(record.contact_email, 0),
        }
        current = grouped.get(key)
        if current is None:
            grouped[key] = candidate
        else:
            current["published_activities"] = max(
                current["published_activities"], candidate["published_activities"]
            )
            for field in ("city", "description", "website"):
                if not current[field] and candidate[field]:
                    current[field] = candidate[field]

    data = list(grouped.values())[:limit]
    return JsonResponse({
        "data": data,
        "meta": {"total": len(grouped), "limit": limit, "generated_at": now.isoformat()},
    })


@require_GET
def community(request):
    """Expose aggregate registration data without publishing volunteer PII."""
    now = timezone.now()
    return JsonResponse({
        "data": {
            "registered_volunteers": Profile.objects.filter(role=Profile.Role.VOLUNTEER).count(),
            "registered_organizers": Profile.objects.filter(role=Profile.Role.ORGANIZER).count(),
            "verified_organizations": OrganizationSubmission.objects.filter(
                status=OrganizationSubmission.Status.VERIFIED
            ).count(),
            "upcoming_published_activities": Kegiatan.objects.filter(
                status_publikasi=Kegiatan.StatusPublikasi.PUBLISHED,
                tanggal_mulai__gte=now,
            ).count(),
        },
        "meta": {"generated_at": now.isoformat()},
    })
