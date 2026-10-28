from django.conf import settings
from django.db import models


class Profile(models.Model):
    class Role(models.TextChoices):
        VOLUNTEER = "volunteer", "Relawan"
        ORGANIZER = "organizer", "Penyelenggara"

    class OrganizationType(models.TextChoices):
        WASTE_BANK = "waste_bank", "Bank sampah"
        ENVIRONMENTAL_COMMUNITY = "environmental_community", "Komunitas lingkungan"
        COMMUNITY_GARDEN = "community_garden", "Kebun komunitas"
        SOCIAL_ORGANIZATION = "social_organization", "Organisasi sosial"
        CAMPUS = "campus", "Kampus"

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.VOLUNTEER)
    phone_number = models.CharField(max_length=20)
    city = models.CharField(max_length=100, blank=True)
    organization_name = models.CharField(max_length=150, blank=True)
    organization_type = models.CharField(max_length=30, choices=OrganizationType.choices, blank=True)

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"


class OrganizationSubmission(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Menunggu verifikasi"
        VERIFIED = "verified", "Terverifikasi"
        REJECTED = "rejected", "Ditolak"

    name = models.CharField(max_length=160)
    type = models.CharField(max_length=120, blank=True)
    contact_email = models.EmailField(blank=True)
    city = models.CharField(max_length=160, blank=True)
    description = models.TextField(blank=True)
    website = models.URLField(blank=True)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.PENDING)
    submitted_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    verified_by = models.CharField(max_length=150, blank=True)

    class Meta:
        ordering = ["status", "-submitted_at"]

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=80, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name
