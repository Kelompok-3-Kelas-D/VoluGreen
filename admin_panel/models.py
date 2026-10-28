from django.conf import settings
from django.db import models

from main.models import Category


class ActivityModeration(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Menunggu tinjauan"
        APPROVED = "approved", "Disetujui"
        REJECTED = "rejected", "Ditolak"

    title = models.CharField(max_length=160)
    organizer_name = models.CharField(max_length=160)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="activities",
    )
    description = models.TextField(blank=True)
    event_date = models.DateField(null=True, blank=True)
    location = models.CharField(max_length=200, blank=True)
    status = models.CharField(
        max_length=12,
        choices=Status.choices,
        default=Status.PENDING,
    )
    moderator_note = models.TextField(blank=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "main_activitymoderation"
        ordering = ["status", "-created_at"]
        verbose_name = "activity moderation record"
        verbose_name_plural = "activity moderation records"

    def __str__(self):
        return self.title


class UserReport(models.Model):
    class Status(models.TextChoices):
        OPEN = "open", "Baru"
        REVIEWING = "reviewing", "Ditinjau"
        RESOLVED = "resolved", "Selesai"

    reporter = models.CharField(max_length=160)
    subject = models.CharField(max_length=200)
    details = models.TextField()
    status = models.CharField(
        max_length=12,
        choices=Status.choices,
        default=Status.OPEN,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "main_userreport"
        ordering = ["status", "-created_at"]

    def __str__(self):
        return self.subject
