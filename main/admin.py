from django.contrib import admin

from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "phone_number", "city")
    list_filter = ("role", "organization_type")
    search_fields = ("user__username", "user__email", "user__first_name")
