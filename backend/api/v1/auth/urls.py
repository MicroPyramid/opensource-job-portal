"""
Authentication URL routing for Job Seekers
"""

from django.urls import path
from rest_framework_simplejwt.views import TokenVerifyView

from . import views

app_name = "auth"

urlpatterns = [
    # Login
    path("login/", views.login, name="login"),
    # Registration & Email Verification
    path("register/", views.register, name="register"),
    path("verify-email/", views.verify_email, name="verify-email"),
    path("resend-verification/", views.resend_verification, name="resend-verification"),
    # Password Management
    path("forgot-password/", views.forgot_password, name="forgot-password"),
    path("reset-password/", views.reset_password, name="reset-password"),
    path("change-password/", views.change_password, name="change-password"),
    path("change-email/", views.change_email, name="change-email"),
    path(
        "verify-email-change/",
        views.verify_email_change,
        name="verify-email-change",
    ),
    # Google OAuth for Job Seekers
    path("google/url/", views.google_auth_url, name="google-auth-url"),
    path("google/callback/", views.google_auth_callback, name="google-callback"),
    path("google/disconnect/", views.google_disconnect, name="google-disconnect"),
    # JWT Token Management
    path(
        "token/refresh/", views.CookieTokenRefreshView.as_view(), name="token-refresh"
    ),
    path("token/verify/", TokenVerifyView.as_view(), name="token-verify"),
    # User Info & Logout
    path("me/", views.current_user, name="current-user"),
    path("logout/", views.logout, name="logout"),
]
