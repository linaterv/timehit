from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .viewsets import ContractorViewSet

router = DefaultRouter()
router.register("contractors", ContractorViewSet, basename="contractor")

urlpatterns = [
    path("", include(router.urls)),
]
