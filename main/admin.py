from django.contrib import admin

from .models import Category, OrganizationSubmission, Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "phone_number", "city")
    list_filter = ("role", "organization_type")
    search_fields = ("user__username", "user__email", "user__first_name")


@admin.register(OrganizationSubmission)
class OrganizationSubmissionAdmin(admin.ModelAdmin):
    list_display = ("name", "type", "city", "status", "submitted_at")
    list_filter = ("status", "type")
    search_fields = ("name", "contact_email", "city")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "updated_at")
    list_filter = ("is_active",)
    search_fields = ("name", "description")


