from django.urls import path
from drf_spectacular.utils import extend_schema
from rest_framework_simplejwt.views import TokenRefreshView

from .views import LoginView, LogoutView, MeView

TokenRefreshView = extend_schema(
    summary="Refresh JWT token",
    description="Submit a valid refresh token to get a new access token.",
)(TokenRefreshView)

urlpatterns = [
    path("login/", LoginView.as_view(), name="auth-login"),
    path("refresh/", TokenRefreshView.as_view(), name="auth-refresh"),
    path("logout/", LogoutView.as_view(), name="auth-logout"),
    path("me/", MeView.as_view(), name="auth-me"),
]
