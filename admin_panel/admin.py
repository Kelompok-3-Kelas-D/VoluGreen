from django.contrib import admin

from .models import ActivityModeration, UserReport


@admin.register(ActivityModeration)
class ActivityModerationAdmin(admin.ModelAdmin):
    list_display = ("title", "organizer_name", "category", "status", "created_at")
    list_filter = ("status", "category")
    search_fields = ("title", "organizer_name", "location")
    readonly_fields = ("reviewed_by", "reviewed_at")


@admin.register(UserReport)
class UserReportAdmin(admin.ModelAdmin):
    list_display = ("subject", "reporter", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("subject", "reporter", "details")
