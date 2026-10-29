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
        impact = getattr(activity, "dampak", None)
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
            "impact_form": DampakForm(instance=impact, auto_id=f"id_%s_{activity.pk}") if can_report_impact else None,
        })
    return {
        "profile": profile,
        "organization_submission": submission,
        "activities": activities,
        "impact_activities": [activity for activity in activities if activity["can_report_impact"]],
        "activity_count": len(activities),
        "draft_count": sum(a["status_publikasi"] == Kegiatan.StatusPublikasi.DRAFT for a in activities),
        "published_count": sum(a["status_publikasi"] == Kegiatan.StatusPublikasi.PUBLISHED for a in activities),
        "needs_report_count": sum(
            a["can_report_impact"] and a["impact_form"].instance.pk is None
            for a in activities
        ),
        "form": form or KegiatanForm(),
    }


@login_required(login_url="/login/")
def dashboard(request, page="overview"):
    profile = _require_organizer(request)
    dashboard_url = reverse("organizer:activities")

    if request.method == "POST":
        action = request.POST.get("action")
        if action in {"submit_activity", "save_activity"}:
            activity_id = request.POST.get("activity_id")
            activity = (get_object_or_404(Kegiatan, pk=activity_id, organizer=request.user)
                        if activity_id else Kegiatan(organizer=request.user))
            if activity.pk and activity.status_publikasi != Kegiatan.StatusPublikasi.DRAFT:
                messages.error(request, "Kegiatan yang sudah terbit atau diarsipkan tidak dapat diedit dari formulir draft.")
                return redirect(f"{dashboard_url}#lowongan")
            form = KegiatanForm(request.POST, instance=activity)
            if form.is_valid():
                with transaction.atomic():
                    activity = form.save(commit=False)
                    activity.organizer = request.user
                    activity.status_publikasi = Kegiatan.StatusPublikasi.DRAFT
                    activity.save()
                messages.success(request, "Kegiatan terkirim untuk ditinjau admin.")
                return redirect(f"{dashboard_url}#lowongan")
            context = _dashboard_context(request, profile, form)
            context["page"] = page
            return render(request, "organizer/dashboard.html", context)

        if action == "delete_activity":
            activity = get_object_or_404(Kegiatan, pk=request.POST.get("activity_id"), organizer=request.user)
            if activity.status_publikasi == Kegiatan.StatusPublikasi.PUBLISHED:
                messages.error(request, "Kegiatan yang sudah terbit tidak dapat dihapus. Hubungi admin untuk mengarsipkannya.")
            else:
                activity.delete()
                messages.success(request, "Draft kegiatan dihapus.")
            return redirect(f"{dashboard_url}#lowongan")

        if action == "save_impact":
            activity = get_object_or_404(Kegiatan, pk=request.POST.get("activity_id"), organizer=request.user)
            if activity.status_publikasi != Kegiatan.StatusPublikasi.PUBLISHED or activity.tanggal_mulai > timezone.now():
                messages.error(request, "Dampak dapat dicatat setelah kegiatan terbit dan waktu kegiatannya terlewati.")
                return redirect(f"{dashboard_url}#dampak")
            impact = DampakKegiatan.objects.filter(kegiatan=activity).first()
            form = DampakForm(request.POST, instance=impact, auto_id=f"id_%s_{activity.pk}")
            if form.is_valid():
                impact = form.save(commit=False)
                impact.kegiatan = activity
                impact.save()
                messages.success(request, "Catatan dampak berhasil disimpan.")
                return redirect(f"{dashboard_url}#dampak")
            else:
                messages.error(request, "Periksa kembali isian dampak yang ditandai.")
                context = _dashboard_context(request, profile)
                for item in context["impact_activities"]:
                    if item["pk"] == activity.pk:
                        item["impact_form"] = form
                        break
                context["page"] = "activities"
                return render(request, "organizer/dashboard.html", context)

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
                return redirect(f"{dashboard_url}#lowongan")
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
                        return redirect(f"{dashboard_url}#lowongan")
                else:
                    application.status = target_status
                if target_status in {PendaftaranRelawan.Status.ACCEPTED, PendaftaranRelawan.Status.REJECTED}:
                    application.pesan = review_note
                    application.save(update_fields=["status", "pesan", "waktu_diperbarui"])
                elif target_status == PendaftaranRelawan.Status.ABSENT:
                    application.save(update_fields=["status", "waktu_diperbarui"])
                messages.success(request, f"Status relawan {application.relawan.get_full_name() or application.relawan.get_username()} diperbarui menjadi {application.get_status_display()}.")
            return redirect(f"{dashboard_url}#lowongan")

        messages.error(request, "Aksi organizer tidak dikenali.")
        return redirect(dashboard_url)

    form = KegiatanForm()
    edit_id = request.GET.get("edit")
    if edit_id:
        activity = get_object_or_404(Kegiatan, pk=edit_id, organizer=request.user)
        if activity.status_publikasi != Kegiatan.StatusPublikasi.DRAFT:
            messages.error(request, "Kegiatan terbit/diarsipkan tidak bisa diedit sebagai draft.")
            return redirect(f"{dashboard_url}#lowongan")
        form = KegiatanForm(instance=activity)
    context = _dashboard_context(request, profile, form)
    context["page"] = page
    return render(request, "organizer/dashboard.html", context)
