"""
Authentication URL routing for Job Seekers
"""
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from . import views

app_name = "auth"

urlpatterns = [
    # Google OAuth for Job Seekers
    path("google/url/", views.google_auth_url, name="google-auth-url"),
    path("google/callback/", views.google_auth_callback, name="google-callback"),
    path("google/disconnect/", views.google_disconnect, name="google-disconnect"),
    # JWT Token Management
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token-verify"),
    # User Info & Logout
    path("me/", views.current_user, name="current-user"),
    path("logout/", views.logout, name="logout"),
]
