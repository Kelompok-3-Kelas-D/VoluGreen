# =====================================================================
# === START BAGIAN MICGUEL (MODUL 3: ALUR RELAWAN / PENDAFTARAN) ======
# =====================================================================
"""
Decorator autentikasi Modul 3.

- Halaman HTML: pengguna yang belum login diarahkan ke halaman login.
  Jika Modul 1 (``main:login``) sudah ter-merge, halaman itu yang dipakai;
  jika belum, dipakai halaman login sementara milik Modul 3
  (``volunteer:masuk``) agar fitur tetap bisa dicoba.
- Endpoint AJAX (``/volunteer/api/...``): dikembalikan JSON HTTP 401,
  bukan redirect HTML, agar mudah ditangani ``fetch()``.
"""
from functools import wraps

from django.contrib.auth.views import redirect_to_login
from django.http import JsonResponse
from django.urls import NoReverseMatch, reverse


def url_login():
    try:
        return reverse("main:login")  # Modul 1 (Autentikasi) jika sudah ter-merge
    except NoReverseMatch:
        return reverse("volunteer:masuk")


def _permintaan_ajax(request):
    return (
        "/api/" in request.path
        or request.headers.get("x-requested-with") == "XMLHttpRequest"
        or "application/json" in request.headers.get("accept", "")
    )


def relawan_login_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if request.user.is_authenticated:
            return view_func(request, *args, **kwargs)
        if _permintaan_ajax(request):
            return JsonResponse(
                {"status": "error", "message": "Silakan login terlebih dahulu."},
                status=401,
            )
        return redirect_to_login(request.get_full_path(), url_login())

    return _wrapped
# =====================================================================
# === END BAGIAN MICGUEL (MODUL 3: ALUR RELAWAN / PENDAFTARAN) ========
# =====================================================================

