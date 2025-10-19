"""
Authentication Serializers for Job Seekers
"""
from rest_framework import serializers
from peeldb.models import User, UserEmail, Google


class GoogleAuthSerializer(serializers.Serializer):
    """Serializer for Google OAuth callback - Job Seekers only"""

    code = serializers.CharField(
        required=True, help_text="Authorization code from Google OAuth"
    )
    redirect_uri = serializers.URLField(
        required=True, help_text="Frontend callback URL that was registered with Google"
    )


class UserSerializer(serializers.ModelSerializer):
    """Job Seeker user profile serializer"""

    user_type_display = serializers.CharField(
        source="get_user_type_display", read_only=True
    )
    is_gp_connected = serializers.BooleanField(read_only=True)
    profile_completion_percentage = serializers.IntegerField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "user_type",
            "user_type_display",
            "photo",
            "profile_pic",
            "is_gp_connected",
            "profile_completion_percentage",
            "mobile",
            "gender",
            "is_active",
            "date_joined",
        ]
        read_only_fields = ["id", "username", "user_type", "date_joined"]


class GoogleAccountSerializer(serializers.ModelSerializer):
    """Google account connection info"""

    class Meta:
        model = Google
        fields = ["google_id", "name", "email", "picture", "verified_email"]
        read_only_fields = fields


class TokenResponseSerializer(serializers.Serializer):
    """JWT token response for successful authentication"""

    access = serializers.CharField(help_text="JWT access token (expires in 1 hour)")
    refresh = serializers.CharField(help_text="JWT refresh token (expires in 7 days)")
    user = UserSerializer(help_text="Authenticated user profile")
    requires_profile_completion = serializers.BooleanField(
        default=False,
        help_text="Whether user needs to complete their profile (< 50%)",
    )
    redirect_to = serializers.CharField(
        required=False, help_text="Suggested redirect path for frontend"
    )
    is_new_user = serializers.BooleanField(
        default=False, help_text="Whether this is a newly created user"
    )


class RefreshTokenSerializer(serializers.Serializer):
    """Token refresh request"""

    refresh = serializers.CharField(help_text="Refresh token from login")


class GoogleUrlRequestSerializer(serializers.Serializer):
    """Request serializer for Google OAuth URL generation"""

    redirect_uri = serializers.URLField(
        required=True, help_text="Frontend callback URL"
    )
