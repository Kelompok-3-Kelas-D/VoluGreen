from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.db import IntegrityError, transaction
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from urllib.parse import urlencode

from .forms import LoginForm, ProfileSettingsForm, RegistrationForm
from organizer.models import Kegiatan

from .models import OrganizationSubmission, Profile


def home(request):
    now = timezone.now()
    activities = list(
        Kegiatan.objects.filter(
            status_publikasi=Kegiatan.StatusPublikasi.PUBLISHED,
            tanggal_mulai__gte=now,
        ).select_related("kategori", "organizer", "organizer__profile")[:6]
    )
    for activity in activities:
        profile = getattr(activity.organizer, "profile", None)
        activity.organizer_name = (
            profile.organization_name
            if profile and profile.organization_name
            else activity.organizer.get_username()
        )

    profile_data = None
    profile = getattr(request.user, "profile", None) if request.user.is_authenticated else None
    if profile:
        submission = OrganizationSubmission.objects.filter(
            contact_email__iexact=request.user.email
        ).first() if profile.role == Profile.Role.ORGANIZER else None
        profile_data = {
            "role": profile.role,
            "name": profile.organization_name if profile.role == Profile.Role.ORGANIZER else (request.user.first_name or request.user.get_username()),
            "email": request.user.email,
            "phone": profile.phone_number,
            "city": profile.city,
            "joined": timezone.localtime(request.user.date_joined).strftime("%d %b %Y"),
            "organization_type": profile.get_organization_type_display(),
            "organization_city": profile.city,
            "organization_description": submission.description if submission else "",
            "organization_status": submission.status if submission else "not_submitted",
        }

    requested_role = request.GET.get("role", Profile.Role.VOLUNTEER)
    if requested_role not in Profile.Role.values:
        requested_role = Profile.Role.VOLUNTEER
    return render(request, "index.html", {
        "volunteer_count": Profile.objects.filter(role=Profile.Role.VOLUNTEER).count(),
        "verified_organization_count": OrganizationSubmission.objects.filter(
            status=OrganizationSubmission.Status.VERIFIED
        ).count(),
        "public_activities": activities,
        "profile_data": profile_data,
        "requested_role": requested_role,
    })


@login_required(login_url="/login/")
def profile_settings(request):
    profile = getattr(request.user, "profile", None)
    if profile is None:
        messages.error(request, "Profil akun belum tersedia.")
        return redirect("main:home")
    submission = OrganizationSubmission.objects.filter(
        contact_email__iexact=request.user.email
    ).first() if profile.role == Profile.Role.ORGANIZER else None
    profile_form = ProfileSettingsForm(
        request.POST if request.method == "POST" and request.POST.get("form_type") == "profile" else None,
        user=request.user, profile=profile, submission=submission,
    )
    password_form = PasswordChangeForm(
        request.user,
        request.POST if request.method == "POST" and request.POST.get("form_type") == "password" else None,
    )

    if request.method == "POST" and request.POST.get("form_type") == "profile" and profile_form.is_valid():
        data = profile_form.cleaned_data
        with transaction.atomic():
            profile.phone_number = data["phone_number"]
            profile.city = data["city"].strip()
            if profile.role == Profile.Role.ORGANIZER:
                profile.organization_name = data["name"].strip()
                profile.organization_type = data["organization_type"]
                if submission is None:
                    submission = OrganizationSubmission.objects.create(
                        name=profile.organization_name,
                        type=profile.get_organization_type_display(),
                        contact_email=request.user.email,
                        city=profile.city,
                        description=data["organization_description"].strip(),
                    )
                else:
                    changed = any((
                        submission.name != profile.organization_name,
                        submission.type != profile.get_organization_type_display(),
                        submission.city != profile.city,
                        submission.description != data["organization_description"].strip(),
                    ))
                    submission.name = profile.organization_name
                    submission.type = profile.get_organization_type_display()
                    submission.city = profile.city
                    submission.description = data["organization_description"].strip()
                    if changed:
                        submission.status = OrganizationSubmission.Status.PENDING
                        submission.verified_at = None
                        submission.verified_by = ""
                    submission.save()
            else:
                request.user.first_name = data["name"].strip()
                request.user.save(update_fields=["first_name"])
            profile.save()
        messages.success(request, "Perubahan profil tersimpan.")
        return redirect("main:profile_settings")

    if request.method == "POST" and request.POST.get("form_type") == "password" and password_form.is_valid():
        password_form.save()
        update_session_auth_hash(request, request.user)
        messages.success(request, "Kata sandi berhasil diperbarui.")
        return redirect("main:profile_settings")

    return render(request, "profile_settings.html", {
        "profile": profile,
        "profile_form": profile_form,
        "password_form": password_form,
        "submission": submission,
    })


def register(request):
    if request.user.is_authenticated:
        return redirect("main:home")
    requested_role = request.GET.get("role")
    if requested_role not in Profile.Role.values:
        requested_role = Profile.Role.VOLUNTEER
    next_url = request.POST.get("next", "") if request.method == "POST" else request.GET.get("next", "")
    if not url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
        next_url = ""
    form = RegistrationForm(request.POST or None, initial={"role": requested_role})
    if request.method == "POST" and form.is_valid():
        try:
            form.save()
        except IntegrityError:
            email = form.cleaned_data["username"]
            if not form._meta.model.objects.filter(username__iexact=email).exists():
                raise
            form.add_error("username", "Email ini sudah terdaftar.")
        else:
            messages.success(request, "Akun berhasil dibuat. Silakan login.")
            login_params = {"role": form.cleaned_data["role"]}
            if next_url:
                login_params["next"] = next_url
            return redirect(f"{reverse('main:login')}?{urlencode(login_params)}")
    return render(request, "register.html", {
        "form": form,
        "requested_role": form.data.get("role", requested_role),
        "next": next_url,
    })


def login_user(request):
    if request.user.is_authenticated:
        return redirect("main:home")
    requested_role = request.GET.get("role", Profile.Role.VOLUNTEER)
    if requested_role not in Profile.Role.values:
        requested_role = Profile.Role.VOLUNTEER
    if request.method == "POST":
        requested_role = request.POST.get("role", requested_role)
        if requested_role not in Profile.Role.values:
            requested_role = Profile.Role.VOLUNTEER
    next_url = request.POST.get("next", "") if request.method == "POST" else request.GET.get("next", "")
    if not url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
        next_url = ""
    form = LoginForm(request, data=request.POST or None, initial={"role": requested_role})
    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        login(request, user)
        selected_role = form.cleaned_data.get("role")
        if not selected_role:
            profile = getattr(user, "profile", None)
            selected_role = profile.role if profile else Profile.Role.VOLUNTEER
        if url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
            destination = next_url
        elif selected_role == Profile.Role.ORGANIZER:
            destination = reverse("organizer:dashboard")
        else:
            destination = reverse("volunteer:halaman_dashboard_relawan")
        response = redirect(destination)
        response.set_cookie("last_login", timezone.localtime().strftime("%Y-%m-%d %H:%M:%S"), samesite="Lax")
        return response
    return render(request, "login.html", {
        "form": form,
        "next": next_url,
        "requested_role": form.data.get("role", requested_role),
        "verified_organization_count": OrganizationSubmission.objects.filter(
            status=OrganizationSubmission.Status.VERIFIED
        ).count(),
    })


def logout_user(request):
    logout(request)
    response = redirect("main:home")
    response.delete_cookie("last_login")
    return response
