from django.urls import path

from . import views

app_name = "mock_api"

urlpatterns = [
    path("activities/", views.activities, name="activities"),
    path("organizers/", views.organizers, name="organizers"),
    path("community/", views.community, name="community"),
]
