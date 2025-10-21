"""
URL routing for Recruiter API (Auth + Team Management)
"""
from django.urls import path
from . import views, auth_views

app_name = "recruiter"

urlpatterns = [
    # ===== AUTHENTICATION =====
    # Registration & Login
    path("auth/register/", auth_views.register, name="register"),
    path("auth/login/", auth_views.login, name="login"),
    path("auth/logout/", auth_views.logout, name="logout"),

    # Email Verification
    path("auth/verify-email/", auth_views.verify_email, name="verify-email"),
    path("auth/resend-verification/", auth_views.resend_verification, name="resend-verification"),

    # Password Management
    path("auth/forgot-password/", auth_views.forgot_password, name="forgot-password"),
    path("auth/reset-password/", auth_views.reset_password, name="reset-password"),
    path("auth/change-password/", auth_views.change_password, name="change-password"),

    # Team Invitation Acceptance
    path("auth/accept-invitation/", auth_views.accept_invitation, name="accept-invitation"),

    # User Info
    path("auth/me/", auth_views.me, name="me"),

    # Google OAuth
    path("auth/google/url/", auth_views.google_auth_url, name="google-auth-url"),
    path("auth/google/callback/", auth_views.google_callback, name="google-callback"),
    path("auth/google/complete/", auth_views.google_complete, name="google-complete"),

    # ===== TEAM MANAGEMENT =====
    # Team Members
    path("team/", views.list_team_members, name="team-list"),
    path("team/<int:user_id>/", views.get_team_member, name="team-detail"),
    path("team/<int:user_id>/update/", views.update_team_member, name="team-update"),
    path("team/<int:user_id>/remove/", views.remove_team_member, name="team-remove"),

    # Team Invitations
    path("team/invite/", views.invite_team_member, name="team-invite"),
    path("team/invitations/", views.list_invitations, name="invitations-list"),
    path("team/invitations/<int:invitation_id>/resend/", views.resend_invitation, name="invitation-resend"),
    path("team/invitations/<int:invitation_id>/cancel/", views.cancel_invitation, name="invitation-cancel"),
]
