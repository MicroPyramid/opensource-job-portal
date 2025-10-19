"""
Authentication Views for Job Seekers
Google OAuth 2.0 integration for modern frontend clients
"""
import requests
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenRefreshView
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes

from peeldb.models import Google
from .serializers import (
    GoogleAuthSerializer,
    TokenResponseSerializer,
    UserSerializer,
    GoogleUrlRequestSerializer,
)
from .utils import create_or_update_google_user, get_tokens_for_user


@extend_schema(
    tags=["Authentication"],
    summary="Get Google OAuth URL",
    description="Generate Google OAuth 2.0 authorization URL for frontend to redirect users.",
    parameters=[
        OpenApiParameter(
            name="redirect_uri",
            type=OpenApiTypes.URI,
            location=OpenApiParameter.QUERY,
            required=True,
            description="Frontend callback URL where Google will redirect after authentication",
            examples=[
                OpenApiExample(
                    "SvelteKit",
                    value="http://localhost:3000/auth/google/callback",
                ),
                OpenApiExample(
                    "React", value="http://localhost:3000/callback"
                ),
            ],
        )
    ],
    responses={
        200: {
            "type": "object",
            "properties": {
                "auth_url": {
                    "type": "string",
                    "description": "Google OAuth authorization URL",
                },
                "user_type": {"type": "string", "description": "User type (always 'JS' for Job Seekers)"},
            },
        }
    },
)
@api_view(["GET"])
@permission_classes([AllowAny])
def google_auth_url(request):
    """
    Generate Google OAuth URL for frontend to redirect users

    **Query Parameters:**
    - `redirect_uri` (required): Frontend callback URL where Google will redirect after auth

    **Response:**
    ```json
    {
        "auth_url": "https://accounts.google.com/o/oauth2/auth?...",
        "user_type": "JS"
    }
    ```

    **Example:**
    ```
    GET /api/v1/auth/google/url/?redirect_uri=http://localhost:3000/auth/google/callback
    ```
    """
    serializer = GoogleUrlRequestSerializer(data=request.query_params)
    serializer.is_valid(raise_exception=True)

    redirect_uri = serializer.validated_data["redirect_uri"]

    # Build Google OAuth URL
    google_auth_url = (
        "https://accounts.google.com/o/oauth2/auth"
        f"?client_id={settings.GOOGLE_CLIENT_ID}"
        "&response_type=code"
        "&scope=https://www.googleapis.com/auth/userinfo.profile "
        "https://www.googleapis.com/auth/userinfo.email"
        f"&redirect_uri={redirect_uri}"
        "&state=JS"  # Job Seeker
        "&access_type=offline"
        "&prompt=consent"
    )

    return Response({"auth_url": google_auth_url, "user_type": "JS"})


@extend_schema(
    tags=["Authentication"],
    summary="Google OAuth Callback",
    description="Exchange Google authorization code for JWT access and refresh tokens. Creates or updates Job Seeker user account.",
    request=GoogleAuthSerializer,
    responses={
        200: TokenResponseSerializer,
        400: {
            "type": "object",
            "properties": {
                "error": {"type": "string"},
                "detail": {"type": "string"},
            },
        },
    },
    examples=[
        OpenApiExample(
            "Success Response",
            value={
                "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
                "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
                "user": {
                    "id": 123,
                    "email": "user@example.com",
                    "first_name": "John",
                    "user_type": "JS",
                    "profile_completion_percentage": 45,
                },
                "requires_profile_completion": True,
                "redirect_to": "/profile/complete",
                "is_new_user": True,
            },
            response_only=True,
            status_codes=["200"],
        )
    ],
)
@api_view(["POST"])
@permission_classes([AllowAny])
def google_auth_callback(request):
    """
    Handle Google OAuth callback for Job Seekers

    **Request Body:**
    ```json
    {
        "code": "auth_code_from_google",
        "redirect_uri": "frontend_callback_url"
    }
    ```

    **Response (Success):**
    ```json
    {
        "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
        "user": {
            "id": 123,
            "email": "user@example.com",
            "first_name": "John",
            "profile_completion_percentage": 45,
            ...
        },
        "requires_profile_completion": true,
        "redirect_to": "/profile/complete",
        "is_new_user": true
    }
    ```

    **Workflow:**
    1. Exchange Google auth code for access token
    2. Fetch user info from Google
    3. Create or update Job Seeker user
    4. Generate JWT tokens
    5. Return tokens + user data + next steps

    **Error Responses:**
    - 400: Invalid code or redirect_uri
    - 400: Failed to exchange code for token
    - 400: Failed to fetch user info from Google
    """
    serializer = GoogleAuthSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    # Exchange code for access token
    token_params = {
        "grant_type": "authorization_code",
        "code": serializer.validated_data["code"],
        "redirect_uri": serializer.validated_data["redirect_uri"],
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
    }

    try:
        token_response = requests.post(
            "https://accounts.google.com/o/oauth2/token", data=token_params, timeout=10
        )
        token_response.raise_for_status()
        token_data = token_response.json()
    except requests.RequestException as e:
        return Response(
            {"error": "Failed to exchange code for token", "detail": str(e)},
            status=status.HTTP_400_BAD_REQUEST,
        )

    access_token = token_data.get("access_token")
    if not access_token:
        return Response(
            {"error": "No access token received"}, status=status.HTTP_400_BAD_REQUEST
        )

    # Get user info from Google
    try:
        user_info_response = requests.get(
            "https://www.googleapis.com/oauth2/v1/userinfo",
            params={"access_token": access_token},
            timeout=10,
        )
        user_info_response.raise_for_status()
        user_document = user_info_response.json()
    except requests.RequestException as e:
        return Response(
            {"error": "Failed to fetch user info", "detail": str(e)},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Create or update Job Seeker user
    try:
        user, created = create_or_update_google_user(user_document)
    except ValueError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # Generate JWT tokens
    tokens = get_tokens_for_user(user)

    # Determine post-auth flow for Job Seekers
    requires_profile_completion = user.profile_completion_percentage < 50
    redirect_to = "/"  # Redirect to home page after successful login

    response_data = {
        "access": tokens["access"],
        "refresh": tokens["refresh"],
        "user": UserSerializer(user).data,
        "requires_profile_completion": requires_profile_completion,
        "redirect_to": redirect_to,
        "is_new_user": created,
    }

    return Response(
        TokenResponseSerializer(response_data).data, status=status.HTTP_200_OK
    )


@extend_schema(
    tags=["Authentication"],
    summary="Disconnect Google Account",
    description="Remove Google OAuth connection from Job Seeker profile.",
    responses={
        200: {
            "type": "object",
            "properties": {"message": {"type": "string"}},
        },
        404: {
            "type": "object",
            "properties": {"error": {"type": "string"}},
        },
    },
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def google_disconnect(request):
    """
    Disconnect Google account from Job Seeker profile

    **Headers:**
    ```
    Authorization: Bearer <access_token>
    ```

    **Response (Success):**
    ```json
    {
        "message": "Google account disconnected successfully"
    }
    ```

    **Response (Error):**
    ```json
    {
        "error": "No Google account connected"
    }
    ```
    """
    user = request.user

    try:
        google_account = Google.objects.get(user=user)
        google_account.delete()
        return Response(
            {"message": "Google account disconnected successfully"},
            status=status.HTTP_200_OK,
        )
    except Google.DoesNotExist:
        return Response(
            {"error": "No Google account connected"}, status=status.HTTP_404_NOT_FOUND
        )


@extend_schema(
    tags=["User Profile"],
    summary="Get Current User",
    description="Retrieve authenticated Job Seeker's profile information.",
    responses={200: UserSerializer, 401: None},
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def current_user(request):
    """
    Get current authenticated Job Seeker profile

    **Headers:**
    ```
    Authorization: Bearer <access_token>
    ```

    **Response:**
    ```json
    {
        "id": 123,
        "email": "user@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "user_type": "JS",
        "user_type_display": "Job Seeker",
        "profile_completion_percentage": 75,
        "is_gp_connected": true,
        ...
    }
    ```
    """
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


@extend_schema(
    tags=["Authentication"],
    summary="Logout",
    description="Logout user by blacklisting refresh token. Access token will remain valid until expiry.",
    request={
        "type": "object",
        "properties": {"refresh": {"type": "string", "description": "Refresh token"}},
        "required": ["refresh"],
    },
    responses={
        200: {
            "type": "object",
            "properties": {"message": {"type": "string"}},
        },
        400: {
            "type": "object",
            "properties": {
                "error": {"type": "string"},
                "detail": {"type": "string"},
            },
        },
    },
)
@api_view(["POST"])
@permission_classes([AllowAny])
def logout(request):
    """
    Logout user by blacklisting refresh token

    **Request Body:**
    ```json
    {
        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
    }
    ```

    **Response:**
    ```json
    {
        "message": "Logout successful"
    }
    ```

    Note: With token blacklisting enabled, the refresh token will be invalidated.
    The access token will still be valid until it expires (1 hour).
    Frontend should delete both tokens from storage.
    """
    try:
        from rest_framework_simplejwt.tokens import RefreshToken

        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response(
                {"error": "Refresh token is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        token = RefreshToken(refresh_token)
        token.blacklist()

        return Response(
            {"message": "Logout successful"}, status=status.HTTP_200_OK
        )
    except Exception as e:
        return Response(
            {"error": "Invalid token", "detail": str(e)},
            status=status.HTTP_400_BAD_REQUEST,
        )
