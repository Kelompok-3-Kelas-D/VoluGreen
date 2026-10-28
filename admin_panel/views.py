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

            # Hapus kategori berdasarkan ID yang dikirim form.
            elif action == "delete_category":
                Category.objects.filter(pk=request.POST.get("category_id")).delete()
                messages.success(request, "Kategori berhasil dihapus.")

            # Setujui atau tolak pendaftaran organisasi.
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
            # Setujui atau tolak kegiatan; sumber menentukan model yang dipakai.
            elif action in {"approve_activity", "reject_activity"}:
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
                messages.success(request, "Keputusan moderasi kegiatan tersimpan.")

            # Ubah status laporan setelah memastikan nilainya valid.
            elif action == "update_report":
                report = UserReport.objects.get(pk=request.POST.get("report_id"))
                report.status = request.POST.get("status")
                if report.status not in UserReport.Status.values:
                    raise ValueError("Status laporan tidak valid.")
                report.save(update_fields=["status"])
                messages.success(request, "Status laporan diperbarui.")

            # Beri pesan error jika form mengirim action yang tidak dikenal.
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


# ---------------------------------------------------------------------------
# REFERENSI LATIHAN LIVE CODING — ADMIN VIEWS
#
# Contoh di bawah sengaja berupa komentar dan tidak dijalankan aplikasi.
# Saat latihan, pindahkan potongan yang diperlukan ke lokasi yang disebutkan,
# hapus tanda komentar (#), dan sesuaikan template jika soal meminta kontrol
# pencarian/filter terlihat di halaman.
# ---------------------------------------------------------------------------

# SOAL 1 — Tambahkan pencarian organisasi berdasarkan nama atau email.
# Lokasi: ganti baris `organizations = OrganizationSubmission.objects.all()`
# di dalam dashboard(). Tambahkan import Q di bagian import atas:
#     from django.db.models import Q
#
#     organizations = OrganizationSubmission.objects.all()
#     query = request.GET.get("q", "").strip()
#     if query:
#         organizations = organizations.filter(
#             Q(name__icontains=query) | Q(contact_email__icontains=query)
#         )
#
# Tambahkan query ke context agar teks pencarian tetap terlihat setelah submit:
#     "organization_query": query,
#
# Lalu aktifkan form GET pada komentar LATIHAN PENCARIAN ORGANISASI di bagian
# Organisasi pada admin_panel/templates/admin_panel/dashboard.html. Form itu
# mengirim `q` ke view dan tetap membuka tab organisasi lewat URL hash.
# Jangan mengubah queryset menjadi list sebelum filter.

# SOAL 2 — Tampilkan laporan yang belum selesai saja.
# Lokasi: ganti nilai "reports" pada dictionary context di dashboard().
#
#     "reports": UserReport.objects.exclude(
#         status=UserReport.Status.RESOLVED
#     ),
#
# Kalau soal meminta filter pilihan status, baca nilainya dari request.GET,
# validasi terhadap UserReport.Status.values, lalu terapkan .filter(status=...).
# Tambahkan juga <select name="report_status"> pada form GET di template.

# SOAL 3 — Wajibkan catatan moderator saat menolak ActivityModeration.
# Lokasi: di cabang `else` pada action approve_activity/reject_activity,
# sebelum mengubah activity.status.
#
#     moderator_note = request.POST.get("moderator_note", "").strip()
#     if action == "reject_activity" and not moderator_note:
#         raise ValueError("Isi alasan penolakan terlebih dahulu.")
#
# Setelah itu gunakan nilai yang sudah dibersihkan:
#     activity.moderator_note = moderator_note
#
# Catatan: template harus mengirim input bernama moderator_note untuk aksi
# penolakan. Periksa juga jenis sumber kegiatan, karena kegiatan organizer
# saat ini memakai model/status berbeda dari ActivityModeration.

# SOAL 4 — Batasi aksi update laporan hanya pada POST.
# Lokasi: di dalam blok `elif action == "update_report":`, sebelum menyimpan.
# Pola ini mirip validasi yang sudah ada pada view:
#
#     new_status = request.POST.get("status", "")
#     if new_status not in UserReport.Status.values:
#         raise ValueError("Status laporan tidak valid.")
#     report.status = new_status
#     report.save(update_fields=["status"])
#
# Form HTML untuk aksi tersebut harus memakai method="post" dan menyertakan
# {% csrf_token %}. Untuk menguji alur, cek juga bahwa redirect kembali ke tab
# laporan, bukan mengirim ulang form saat halaman di-refresh.

# SOAL 5 — Tambahkan paginasi pada daftar organisasi.
# Lokasi: setelah queryset organizations selesai difilter dan sebelum context.
# Tambahkan import di bagian atas:
#     from django.core.paginator import Paginator
#
#     organizations_page = Paginator(organizations, 10).get_page(
#         request.GET.get("page")
#     )
#
# Lalu ubah context menjadi:
#     "organizations": organizations_page,
#
# Template perlu menampilkan tombol halaman berikut/sebelumnya dengan
# organizations.has_previous, organizations.previous_page_number,
# organizations.has_next, dan organizations.next_page_number. Pertahankan
# parameter pencarian pada link paginasi agar pencarian tidak hilang.
