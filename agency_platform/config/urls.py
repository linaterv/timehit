from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    # API
    path("api/", include("apps.users.api.urls")),
    path("api/", include("apps.contractors.api.urls")),
    path("api/", include("apps.clients.api.urls")),
    path("api/", include("apps.contracts.api.urls")),
    # HTML views
    path("users/", include("apps.users.management_urls")),
    path("contractors/", include("apps.contractors.urls")),
    path("clients/", include("apps.clients.urls")),
    path("contracts/", include("apps.contracts.urls")),
    path("", include("apps.users.urls")),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
