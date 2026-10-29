from django.urls import path

from . import views

app_name = "admin_panel"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("setup/", views.setup_admin, name="setup_admin"),
]
