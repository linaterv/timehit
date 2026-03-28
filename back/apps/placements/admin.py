from django.contrib import admin

from .models import Placement


@admin.register(Placement)
class PlacementAdmin(admin.ModelAdmin):
    list_display = ("contractor", "client", "client_rate", "contractor_rate", "start_date", "is_active")
    list_filter = ("is_active", "approval_mode")
    search_fields = ("contractor__user__email", "client__name")
