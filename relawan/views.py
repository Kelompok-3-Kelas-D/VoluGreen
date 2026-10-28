from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError, transaction
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from urllib.parse import urlencode
from django.utils import timezone
from django.views.decorators.http import require_POST

from main.models import Profile
from organizer.models import Kegiatan

from .models import PendaftaranKegiatan


def _require_volunteer(request):
    profile = getattr(request.user, "profile", None)
    if profile is None or profile.role != Profile.Role.VOLUNTEER:
        raise PermissionDenied("Fitur ini hanya tersedia untuk akun relawan.")
    return profile


@login_required(login_url="/login/")
def dashboard(request):
    profile = _require_volunteer(request)
    applications = PendaftaranKegiatan.objects.filter(
        relawan=request.user
    ).select_related("kegiatan", "kegiatan__kategori", "kegiatan__organizer")
    return render(request, "relawan/dashboard.html", {
        "profile": profile,
        "applications": applications,
        "active_count": applications.filter(status__in=[
            PendaftaranKegiatan.Status.PENDING,
            PendaftaranKegiatan.Status.ACCEPTED,
        ]).count(),
        "history_count": applications.filter(status__in=[
            PendaftaranKegiatan.Status.ATTENDED,
            PendaftaranKegiatan.Status.ABSENT,
        ]).count(),
        "now": timezone.now(),
    })


@require_POST
def apply(request, kegiatan_id):
    if not request.user.is_authenticated:
        login_url = reverse("main:login") + "?" + urlencode({"next": reverse("eksplorasi:index")})
        return redirect(login_url)
    _require_volunteer(request)
    with transaction.atomic():
        activity = get_object_or_404(
            Kegiatan.objects.select_for_update(),
            pk=kegiatan_id,
            status_publikasi=Kegiatan.StatusPublikasi.PUBLISHED,
            tanggal_mulai__gt=timezone.now(),
        )
        application = PendaftaranKegiatan.objects.filter(
            relawan=request.user, kegiatan=activity
        ).first()
        if application and application.status not in {
            PendaftaranKegiatan.Status.CANCELLED,
            PendaftaranKegiatan.Status.REJECTED,
        }:
            messages.info(request, f"Pendaftaranmu sudah tercatat: {application.get_status_display()}.")
        else:
            occupied = PendaftaranKegiatan.objects.filter(
                kegiatan=activity,
                status__in=[PendaftaranKegiatan.Status.PENDING, PendaftaranKegiatan.Status.ACCEPTED],
            ).count()
            if occupied >= activity.kuota:
                messages.error(request, "Kuota kegiatan sudah penuh.")
            else:
                try:
                    if application:
                        application.status = PendaftaranKegiatan.Status.PENDING
                        application.pesan = ""
                        application.save(update_fields=["status", "pesan", "diperbarui_pada"])
                    else:
                        PendaftaranKegiatan.objects.create(
                            relawan=request.user,
                            kegiatan=activity,
                        )
                except IntegrityError:
                    messages.info(request, "Pendaftaranmu sudah tercatat.")
                else:
                    messages.success(request, f"Pendaftaran ke “{activity.nama}” terkirim. Pantau statusnya di halaman Pendaftaran saya.")
    return redirect("eksplorasi:index")


@require_POST
def cancel(request, pendaftaran_id):
    if not request.user.is_authenticated:
        login_url = reverse("main:login") + "?" + urlencode({"next": reverse("relawan:dashboard")})
        return redirect(login_url)
    _require_volunteer(request)
    application = get_object_or_404(
        PendaftaranKegiatan.objects.select_related("kegiatan"),
        pk=pendaftaran_id,
        relawan=request.user,
    )
    if not application.dapat_dibatalkan:
        messages.error(request, "Pendaftaran ini sudah tidak dapat dibatalkan.")
    elif application.kegiatan.tanggal_mulai <= timezone.now():
        messages.error(request, "Pendaftaran tidak dapat dibatalkan setelah kegiatan dimulai.")
    else:
        application.status = PendaftaranKegiatan.Status.CANCELLED
        application.save(update_fields=["status", "diperbarui_pada"])
        messages.success(request, f"Pendaftaran “{application.kegiatan.nama}” dibatalkan. Kuota tersedia kembali.")
    return redirect("relawan:dashboard")
