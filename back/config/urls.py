from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    path("api/auth/", include("apps.users.urls")),
    path("api/", include("apps.users.api_urls")),
    path("api/", include("apps.audit.urls")),
    path("api/", include("apps.clients.urls")),
    path("api/", include("apps.contractors.urls")),
    path("api/", include("apps.placements.urls")),
]
