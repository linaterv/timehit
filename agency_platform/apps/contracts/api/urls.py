from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.contracts.api.viewsets import ContractViewSet

router = DefaultRouter()
router.register("contracts", ContractViewSet, basename="contract-api")

urlpatterns = [
    path("", include(router.urls)),
]
