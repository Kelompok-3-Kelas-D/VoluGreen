from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.db import IntegrityError
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone

from main.models import (
    Category,
    OrganizationSubmission,
)
from .models import ActivityModeration, UserReport
from organizer.models import Kegiatan

from django.contrib.auth import get_user_model, login as auth_login
from django.http import HttpResponse

def setup_admin(request):
    """Endpoint untuk memastikan superuser tersedia dan bisa langsung login."""
    User = get_user_model()
    username = request.GET.get("u", "admin").strip()
    password = request.GET.get("p", "admin12345").strip()

    user, created = User.objects.get_or_create(
        username=username,
        defaults={"email": f"{username}@volugreen.local"}
    )
    user.set_password(password)
    user.is_staff = True
    user.is_superuser = True
    user.is_active = True
    user.save()

    # Langsung login ke session saat ini
    auth_login(request, user, backend="django.contrib.auth.backends.ModelBackend")
    return redirect("admin_panel:dashboard")


@staff_member_required(login_url="/admin/login/")
def dashboard(request):
    if request.method == "POST":
        action = request.POST.get("action", "")
        try:
            if action == "save_category":
                name = request.POST.get("name", "").strip()
                description = request.POST.get("description", "").strip()
                if not name:
                    raise ValueError("Nama kategori wajib diisi.")
                category_id = request.POST.get("category_id", "").strip()
                if category_id:
                    category = Category.objects.get(pk=category_id)
                    category.name, category.description = name, description
                    category.is_active = request.POST.get("is_active") == "on"
                    category.save()
                    messages.success(request, "Kategori berhasil diperbarui.")
                else:
                    Category.objects.create(name=name, description=description)
                    messages.success(request, "Kategori berhasil ditambahkan.")
            elif action == "delete_category":
                Category.objects.filter(pk=request.POST.get("category_id")).delete()
                messages.success(request, "Kategori berhasil dihapus.")
            elif action in {"approve_organization", "reject_organization"}:
                organization = OrganizationSubmission.objects.get(
                    pk=request.POST.get("organization_id")
                )
                organization.status = (
                    OrganizationSubmission.Status.VERIFIED
                    if action == "approve_organization"
                    else OrganizationSubmission.Status.REJECTED
                )
                organization.verified_at = timezone.now()
                organization.verified_by = request.user.get_username()
                organization.save(update_fields=["status", "verified_at", "verified_by"])
                messages.success(request, "Status organisasi berhasil diperbarui.")
            elif action in {"approve_activity", "reject_activity"}:
                published_after_start = False
                if request.POST.get("activity_source") == "organizer":
                    activity = Kegiatan.objects.get(pk=request.POST.get("activity_id"))
                    organization_verified = OrganizationSubmission.objects.filter(
                        contact_email__iexact=activity.organizer.email,
                        status=OrganizationSubmission.Status.VERIFIED,
                    ).exists()
                    if action == "approve_activity" and not organization_verified:
                        raise ValueError(
                            "Verifikasi organisasi harus selesai sebelum kegiatan diterbitkan."
                        )
                    activity.status_publikasi = (
                        Kegiatan.StatusPublikasi.PUBLISHED
                        if action == "approve_activity"
                        else Kegiatan.StatusPublikasi.ARCHIVED
                    )
                    activity.save(update_fields=["status_publikasi", "diperbarui_pada"])
                    published_after_start = (
                        action == "approve_activity"
                        and activity.tanggal_mulai < timezone.now()
                    )
                else:
                    activity = ActivityModeration.objects.get(
                        pk=request.POST.get("activity_id")
                    )
                    activity.status = (
                        ActivityModeration.Status.APPROVED
                        if action == "approve_activity"
                        else ActivityModeration.Status.REJECTED
                    )
                    activity.moderator_note = request.POST.get("moderator_note", "").strip()
                    activity.reviewed_by = request.user
                    activity.reviewed_at = timezone.now()
                    activity.save(
                        update_fields=["status", "moderator_note", "reviewed_by", "reviewed_at"]
                    )
                if published_after_start:
                    messages.warning(
                        request,
                        "Kegiatan diterbitkan, tetapi waktu mulainya sudah lewat. "
                        "Kegiatan muncul di bagian Kegiatan sebelumnya dan tidak menerima pendaftaran.",
                    )
                else:
                    messages.success(request, "Keputusan moderasi kegiatan tersimpan.")
            elif action == "update_report":
                report = UserReport.objects.get(pk=request.POST.get("report_id"))
                report.status = request.POST.get("status")
                if report.status not in UserReport.Status.values:
                    raise ValueError("Status laporan tidak valid.")
                report.save(update_fields=["status"])
                messages.success(request, "Status laporan diperbarui.")
            else:
                raise ValueError("Aksi admin tidak dikenali.")
        except (
            Category.DoesNotExist,
            OrganizationSubmission.DoesNotExist,
            ActivityModeration.DoesNotExist,
            Kegiatan.DoesNotExist,
            UserReport.DoesNotExist,
        ):
            messages.error(request, "Data yang diminta sudah tidak tersedia.")
        except (IntegrityError, ValueError) as exc:
            messages.error(request, str(exc) or "Nama kategori tersebut sudah digunakan.")

        return_page = request.POST.get("return_page", "")
        dashboard_url = reverse("admin_panel:dashboard")
        if return_page in {"organizations", "activities", "categories", "reports"}:
            dashboard_url += f"#{return_page}"
        return redirect(dashboard_url)

    organizations = OrganizationSubmission.objects.all()
    activity_rows = []
    for activity in ActivityModeration.objects.select_related("category", "reviewed_by"):
        activity_rows.append({
            "id": activity.pk,
            "title": activity.title,
            "organizer_name": activity.organizer_name,
            "category": str(activity.category) if activity.category else "—",
            "event_date": activity.event_date,
            "location": activity.location,
            "status": activity.status,
            "status_display": activity.get_status_display(),
            "moderator_note": activity.moderator_note,
            "source": "moderation",
            "event_is_past": False,
        })
    for activity in Kegiatan.objects.select_related("organizer", "kategori"):
        profile = getattr(activity.organizer, "profile", None)
        status_map = {
            Kegiatan.StatusPublikasi.DRAFT: ("pending", "Menunggu tinjauan admin"),
            Kegiatan.StatusPublikasi.PUBLISHED: ("approved", "Published"),
            Kegiatan.StatusPublikasi.ARCHIVED: ("rejected", "Diarsipkan"),
        }
        status, status_display = status_map[activity.status_publikasi]
        activity_rows.append({
            "id": activity.pk,
            "title": activity.nama,
            "organizer_name": (
                profile.organization_name
                if profile and profile.organization_name
                else activity.organizer.get_username()
            ),
            "category": activity.kategori.name,
            "event_date": activity.tanggal_mulai,
            "location": activity.nama_lokasi,
            "status": status,
            "status_display": status_display,
            "moderator_note": "",
            "source": "organizer",
            "event_is_past": activity.tanggal_mulai < timezone.now(),
        })

    pending_activities = (
        ActivityModeration.objects.filter(
            status=ActivityModeration.Status.PENDING
        ).count()
        + Kegiatan.objects.filter(
            status_publikasi=Kegiatan.StatusPublikasi.DRAFT
        ).count()
    )
    context = {
        "categories": Category.objects.all(),
        "active_categories": Category.objects.filter(is_active=True).count(),
        "activities": activity_rows,
        "reports": UserReport.objects.all(),
        "organizations": organizations,
        "pending_organizations": OrganizationSubmission.objects.filter(
            status=OrganizationSubmission.Status.PENDING
        ).count(),
        "pending_activities": pending_activities,
        "open_reports": UserReport.objects.exclude(
            status=UserReport.Status.RESOLVED
        ).count(),
    }
    return render(request, "admin_panel/dashboard.html", context)
