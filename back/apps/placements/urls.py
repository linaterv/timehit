from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .viewsets import PlacementViewSet

router = DefaultRouter()
router.register("placements", PlacementViewSet, basename="placement")

urlpatterns = [
    path("", include(router.urls)),
]
