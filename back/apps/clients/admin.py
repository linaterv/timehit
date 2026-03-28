from django.contrib import admin

from .models import Client


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("name", "contact_email", "contact_phone", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "contact_email")
