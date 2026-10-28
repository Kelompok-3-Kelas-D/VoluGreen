from django.urls import path

from . import views

app_name = "organizer"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("kegiatan/", views.dashboard, {"page": "activities"}, name="activities"),
]
