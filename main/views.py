from django.contrib import messages
from django.contrib.auth import login, logout
from django.db import IntegrityError
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone

from .forms import LoginForm, RegistrationForm
from .models import Profile


MONTH_NAMES = (
    "",
    "Januari",
    "Februari",
    "Maret",
    "April",
    "Mei",
    "Juni",
    "Juli",
    "Agustus",
    "September",
    "Oktober",
    "November",
    "Desember",
)


def _profile_data(user):
    if not user.is_authenticated:
        return None

    profile = getattr(user, "profile", None)
    if profile is None:
        return None

    joined = timezone.localtime(user.date_joined)
    common_data = {
        "role": profile.role,
        "email": user.email,
        "phone": profile.phone_number,
        "joined": f"{MONTH_NAMES[joined.month]} {joined.year}",
    }

    if profile.role == Profile.Role.ORGANIZER:
        return {
            **common_data,
            "name": profile.organization_name,
            "organization_type": profile.get_organization_type_display(),
        }

    return {
        **common_data,
        "name": user.first_name or user.username,
        "city": profile.city,
        "bio": "",
        "interests": [],
        "avatar": None,
    }


def home(request):
    context = {
        "last_login": request.COOKIES.get(
            "last_login",
            "Belum ada sesi login",
        ),
        "profile_data": _profile_data(request.user),
    }
    return render(request, "index.html", context)


def register(request):
    if request.user.is_authenticated:
        return redirect("main:home")

    form = RegistrationForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        try:
            form.save()
        except IntegrityError:
            # Validasi form dan penyimpanan adalah dua operasi terpisah. Jika dua
            # request dengan email yang sama lolos validasi secara bersamaan,
            # database tetap menjadi sumber kebenaran dan menolak request kedua.
            email = form.cleaned_data["username"]
            if not form._meta.model.objects.filter(username__iexact=email).exists():
                raise
            form.add_error("username", "Email ini sudah terdaftar.")
        else:
            messages.success(
                request,
                "Akun berhasil dibuat. Silakan login.",
            )
            return redirect("main:login")

    return render(request, "register.html", {"form": form})


def login_user(request):
    if request.user.is_authenticated:
        return redirect("main:home")

    form = LoginForm(
        request,
        data=request.POST or None,
    )

    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        login(request, user)

        selected_role = form.cleaned_data.get("role")
        if not selected_role:
            profile = getattr(user, "profile", None)
            selected_role = profile.role if profile else Profile.Role.VOLUNTEER
        if selected_role == Profile.Role.ORGANIZER:
            destination = f'{reverse("main:home")}#organisasi'
        else:
            destination = f'{reverse("main:home")}#profil'

        response = redirect(destination)
        response.set_cookie(
            "last_login",
            timezone.localtime().strftime("%Y-%m-%d %H:%M:%S"),
            samesite="Lax",
        )
        return response

    return render(request, "login.html", {"form": form})


def logout_user(request):
    logout(request)

    response = redirect("main:home")
    response.delete_cookie("last_login")
    return response
