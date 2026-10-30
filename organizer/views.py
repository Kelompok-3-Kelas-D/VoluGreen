from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from main.models import OrganizationSubmission, Profile
from volunteer.models import PendaftaranRelawan

from .forms import DampakForm, KegiatanForm
from .models import DampakKegiatan, Kegiatan


def _require_organizer(request):
    profile = getattr(request.user, "profile", None)
    if profile is None or profile.role != Profile.Role.ORGANIZER:
        raise PermissionDenied("Halaman ini hanya untuk akun penyelenggara.")
    return profile


def _dashboard_context(request, profile, form=None):
    submission = OrganizationSubmission.objects.filter(contact_email__iexact=request.user.email).first()
    activities = []
    for activity in Kegiatan.objects.filter(organizer=request.user).select_related("kategori").prefetch_related("dampak"):
        applications = list(
            PendaftaranRelawan.objects.filter(kegiatan=activity)
            .select_related("relawan", "relawan__profile")
            .order_by("status", "waktu_daftar")
        )
        can_report_impact = (
            activity.status_publikasi == Kegiatan.StatusPublikasi.PUBLISHED
            and activity.tanggal_mulai <= timezone.now()
        )
        activities.append({
            "pk": activity.pk, "nama": activity.nama, "deskripsi": activity.deskripsi,
            "kategori": activity.kategori, "tanggal_mulai": activity.tanggal_mulai,
            "nama_lokasi": activity.nama_lokasi, "kota": activity.kota,
            "kuota": activity.kuota, "sisa_kuota": activity.sisa_kuota,
            "applications": applications,
            "application_count": len(applications),
            "pending_application_count": sum(app.status == PendaftaranRelawan.Status.PENDING for app in applications),
            "event_is_over": activity.tanggal_mulai <= timezone.now(),
            "status_publikasi": activity.status_publikasi,
            "status_display": (
                "Menunggu tinjauan admin"
                if activity.status_publikasi == Kegiatan.StatusPublikasi.DRAFT
                else activity.get_status_publikasi_display()
            ),
            "can_report_impact": can_report_impact,
            "has_impact": hasattr(activity, "dampak"),
        })
    return {
        "profile": profile,
        "organization_submission": submission,
        "activities": activities,
        "pending_activities": [activity for activity in activities if activity["status_publikasi"] == Kegiatan.StatusPublikasi.DRAFT],
        "published_activities": [activity for activity in activities if activity["status_publikasi"] == Kegiatan.StatusPublikasi.PUBLISHED],
        "archived_activities": [activity for activity in activities if activity["status_publikasi"] == Kegiatan.StatusPublikasi.ARCHIVED],
        "activity_count": len(activities),
        "draft_count": sum(a["status_publikasi"] == Kegiatan.StatusPublikasi.DRAFT for a in activities),
        "published_count": sum(a["status_publikasi"] == Kegiatan.StatusPublikasi.PUBLISHED for a in activities),
        "needs_report_count": sum(
            a["can_report_impact"] and not a["has_impact"]
            for a in activities
        ),
        "form": form or KegiatanForm(),
    }


@login_required(login_url="/login/")
def dashboard(request, page="overview"):
    profile = _require_organizer(request)
    dashboard_url = reverse("organizer:dashboard")

    if request.method == "POST":
        action = request.POST.get("action")
        if action in {"submit_activity", "save_activity"}:
            activity_id = request.POST.get("activity_id")
            activity = (get_object_or_404(Kegiatan, pk=activity_id, organizer=request.user)
                        if activity_id else Kegiatan(organizer=request.user))
            if activity.pk and activity.status_publikasi != Kegiatan.StatusPublikasi.DRAFT:
                messages.error(request, "Kegiatan yang sudah terbit atau diarsipkan tidak dapat diedit dari formulir draft.")
                return redirect(f"{dashboard_url}#menunggu")
            form = KegiatanForm(request.POST, instance=activity)
            if form.is_valid():
                with transaction.atomic():
                    activity = form.save(commit=False)
                    activity.organizer = request.user
                    activity.status_publikasi = Kegiatan.StatusPublikasi.DRAFT
                    activity.save()
                messages.success(request, "Kegiatan terkirim untuk ditinjau admin.")
                return redirect(f"{dashboard_url}#menunggu")
            context = _dashboard_context(request, profile, form)
            context["page"] = "activities"
            context["editing_activity_id"] = activity.pk
            return render(request, "organizer/dashboard.html", context)

        if action == "delete_activity":
            activity = get_object_or_404(Kegiatan, pk=request.POST.get("activity_id"), organizer=request.user)
            if activity.status_publikasi == Kegiatan.StatusPublikasi.DRAFT:
                activity.delete()
                messages.success(request, "Draft kegiatan dihapus.")
            else:
                messages.error(request, "Hanya kegiatan yang menunggu tinjauan yang dapat dihapus.")
            return redirect(f"{dashboard_url}#menunggu")

        if action == "update_application":
            application = get_object_or_404(
                PendaftaranRelawan.objects.select_related("kegiatan"),
                pk=request.POST.get("application_id"),
                kegiatan__organizer=request.user,
            )
            target_status = request.POST.get("status")
            review_note = request.POST.get("pesan", "").strip()
            if len(review_note) > 500:
                messages.error(request, "Catatan penyelenggara maksimal 500 karakter.")
                return redirect(f"{dashboard_url}#kegiatan-{application.kegiatan_id}")
            event_is_over = application.kegiatan.tanggal_mulai <= timezone.now()
            if target_status == PendaftaranRelawan.Status.ACCEPTED:
                allowed = application.status == PendaftaranRelawan.Status.PENDING and not event_is_over
            elif target_status == PendaftaranRelawan.Status.REJECTED:
                allowed = application.status in {PendaftaranRelawan.Status.PENDING, PendaftaranRelawan.Status.ACCEPTED} and not event_is_over
            elif target_status in {PendaftaranRelawan.Status.COMPLETED, PendaftaranRelawan.Status.ABSENT}:
                allowed = application.status == PendaftaranRelawan.Status.ACCEPTED and event_is_over
            else:
                allowed = False
            if not allowed:
                messages.error(request, "Status pendaftaran tidak dapat diubah ke pilihan tersebut.")
            else:
                if target_status == PendaftaranRelawan.Status.COMPLETED:
                    try:
                        application.tandai_selesai(
                            jam_kontribusi=request.POST.get("jam_kontribusi", 3),
                            catatan_dampak=request.POST.get("catatan_dampak", ""),
                        )
                    except ValidationError as exc:
                        messages.error(request, "; ".join(exc.messages))
                        return redirect(f"{dashboard_url}#kegiatan-{application.kegiatan_id}")
                else:
                    application.status = target_status
                if target_status in {PendaftaranRelawan.Status.ACCEPTED, PendaftaranRelawan.Status.REJECTED}:
                    application.pesan = review_note
                    application.save(update_fields=["status", "pesan", "waktu_diperbarui"])
                elif target_status == PendaftaranRelawan.Status.ABSENT:
                    application.save(update_fields=["status", "waktu_diperbarui"])
                messages.success(request, f"Status relawan {application.relawan.get_full_name() or application.relawan.get_username()} diperbarui menjadi {application.get_status_display()}.")
            return redirect(f"{dashboard_url}#kegiatan-{application.kegiatan_id}")

        messages.error(request, "Aksi organizer tidak dikenali.")
        return redirect(dashboard_url)

    form = KegiatanForm()
    edit_id = request.GET.get("edit") if page == "activities" else None
    if edit_id:
        activity = get_object_or_404(Kegiatan, pk=edit_id, organizer=request.user)
        if activity.status_publikasi != Kegiatan.StatusPublikasi.DRAFT:
            messages.error(request, "Kegiatan terbit/diarsipkan tidak bisa diedit sebagai draft.")
            return redirect(f"{dashboard_url}#menunggu")
        form = KegiatanForm(instance=activity)
    context = _dashboard_context(request, profile, form)
    context["page"] = page
    context["editing_activity_id"] = activity.pk if edit_id else None
    return render(request, "organizer/dashboard.html", context)


@login_required(login_url="/login/")
def impact_detail(request, pk):
    profile = _require_organizer(request)
    activity = get_object_or_404(Kegiatan.objects.select_related("kategori"), pk=pk, organizer=request.user)
    can_report = activity.status_publikasi == Kegiatan.StatusPublikasi.PUBLISHED and activity.tanggal_mulai <= timezone.now()
    impact = DampakKegiatan.objects.filter(kegiatan=activity).first()
    form = DampakForm(request.POST or None, instance=impact, auto_id=f"id_%s_{activity.pk}")
    if request.method == "POST":
        if not can_report:
            messages.error(request, "Dampak dapat dicatat setelah kegiatan terbit dan waktu kegiatannya terlewati.")
            return redirect("organizer:impact_detail", pk=pk)
        if form.is_valid():
            report = form.save(commit=False)
            report.kegiatan = activity
            report.save()
            messages.success(request, "Laporan dampak kegiatan berhasil disimpan.")
            return redirect("organizer:impact_detail", pk=pk)
    return render(request, "organizer/impact_detail.html", {
        "profile": profile, "activity": activity, "form": form, "page": "impact",
        "can_report": can_report, "impact": impact,
    })
