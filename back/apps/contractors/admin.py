from django.contrib import admin

from .models import Contractor


@admin.register(Contractor)
class ContractorAdmin(admin.ModelAdmin):
    list_display = ("user", "hourly_rate_default", "phone", "is_active")
    list_filter = ("is_active",)
    search_fields = ("user__email", "user__first_name", "user__last_name")
