"""URL patterns for admin user management UI (S003)."""
from django.urls import path

from apps.users import management_views as views

urlpatterns = [
    path("", views.user_list, name="user-list"),
    path("create/", views.user_create, name="user-create"),
    path("<uuid:pk>/edit/", views.user_edit, name="user-edit"),
    path("<uuid:pk>/deactivate/", views.user_deactivate, name="user-deactivate"),
    path("<uuid:pk>/reset-password/", views.user_reset_password, name="user-reset-password"),
]
