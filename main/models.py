from django.conf import settings
from django.db import models


class Profile(models.Model):
    class Role(models.TextChoices):
        VOLUNTEER = "volunteer", "Relawan"
        ORGANIZER = "organizer", "Penyelenggara"

    class OrganizationType(models.TextChoices):
        WASTE_BANK = "waste_bank", "Bank sampah"
        ENVIRONMENTAL_COMMUNITY = (
            "environmental_community",
            "Komunitas lingkungan",
        )
        COMMUNITY_GARDEN = "community_garden", "Kebun komunitas"
        SOCIAL_ORGANIZATION = "social_organization", "Organisasi sosial"
        CAMPUS = "campus", "Kampus"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.VOLUNTEER,
    )
    phone_number = models.CharField(max_length=20)
    city = models.CharField(max_length=100, blank=True)
    organization_name = models.CharField(max_length=150, blank=True)
    organization_type = models.CharField(
        max_length=30,
        choices=OrganizationType.choices,
        blank=True,
    )

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"
