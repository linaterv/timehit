"""URL patterns for contract management UI (S007)."""
from django.urls import path

from apps.contracts import views

urlpatterns = [
    path("", views.contract_list, name="contract-list"),
    path("create/", views.contract_create, name="contract-create"),
    path("<uuid:pk>/", views.contract_detail, name="contract-detail"),
    path("<uuid:pk>/edit/", views.contract_edit, name="contract-edit"),
    path("<uuid:pk>/download/", views.contract_download, name="contract-download"),
]
