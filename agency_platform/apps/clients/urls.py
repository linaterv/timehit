"""URL patterns for client management UI (S005)."""
from django.urls import path

from apps.clients import views

urlpatterns = [
    path("", views.client_list, name="client-list"),
    path("create/", views.client_create, name="client-create"),
    path("<uuid:pk>/edit/", views.client_edit, name="client-edit"),
    path("<uuid:pk>/deactivate/", views.client_deactivate, name="client-deactivate"),
]
