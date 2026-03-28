"""URL patterns for contractor management UI (S004)."""
from django.urls import path

from apps.contractors import views

urlpatterns = [
    path("", views.contractor_list, name="contractor-list"),
    path("create/", views.contractor_create, name="contractor-create"),
    path("<int:pk>/edit/", views.contractor_edit, name="contractor-edit"),
    path("<int:pk>/deactivate/", views.contractor_deactivate, name="contractor-deactivate"),
    path("my-profile/", views.contractor_own_profile, name="contractor-own-profile"),
]
