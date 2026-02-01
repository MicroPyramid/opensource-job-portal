"""
Authentication Views for Job Seekers
Google OAuth 2.0 integration for modern frontend clients
"""
import requests
from django.conf import settings
from django.utils.crypto import get_random_string
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
    ChangePasswordSerializer,
    RegisterSerializer,
    VerifyEmailSerializer,
    ResendVerificationSerializer,
    ForgotPasswordSerializer,
    ResetPasswordSerializer,
)
from .utils import create_or_update_google_user, get_tokens_for_user
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken


def send_verification_email(user, request):
    """Send email verification link for job seeker"""
    from datetime import datetime
    from django.template import loader
    from dashboard.tasks import send_email

    # Use site UI URL for verification
    frontend_url = settings.SITE_FRONTEND_URL if hasattr(settings, 'SITE_FRONTEND_URL') else 'http://localhost:5173'
    verification_url = f"{frontend_url}/verify-email/?token={user.activation_code}"

    # Render email template
    template = loader.get_template('jobseeker/email/verification.html')
    context = {
        'user': user,
        'verification_url': verification_url,
        'current_year': datetime.now().year
    }
    html_content = template.render(context)

    # Send email via Celery task
    send_email.delay(
        mto=[user.email],
        msubject="Verify your PeelJobs account",
        mbody=html_content
    )


def send_password_reset_email(user, request):
    """Send password reset link for job seeker"""
    from datetime import datetime
    from django.template import loader
    from dashboard.tasks import send_email

    # Use site UI URL for password reset
    frontend_url = settings.SITE_FRONTEND_URL if hasattr(settings, 'SITE_FRONTEND_URL') else 'http://localhost:5173'
    reset_url = f"{frontend_url}/reset-password/?token={user.activation_code}"

    # Render email template
    template = loader.get_template('jobseeker/email/password_reset.html')
    context = {
        'user': user,
        'reset_url': reset_url,
        'current_year': datetime.now().year
    }
    html_content = template.render(context)

    # Send email via Celery task
    send_email.delay(
        mto=[user.email],
        msubject="Reset your PeelJobs password",
        mbody=html_content
    )


@extend_schema(
    tags=["Authentication"],
    summary="Register New Job Seeker",
    description="Create new job seeker account with email and password",
    request=RegisterSerializer,
)
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """
    Register new job seeker account

    Creates user and sends verification email
    """
    serializer = RegisterSerializer(data=request.data)

    if serializer.is_valid():
        result = serializer.save()
        user = result['user']

        # Send verification email
        try:
            send_verification_email(user, request)
        except Exception as e:
            # Log error but don't fail registration
            print(f"Failed to send verification email: {e}")

        return Response({
            "success": True,
            "user": {
                "id": user.id,
                "email": user.email,
                "user_type": user.user_type,
                "is_active": user.is_active
            },
            "message": "Registration successful. Please check your email to verify your account."
        }, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=["Authentication"],
    summary="Verify Email",
    description="Verify job seeker email with token from verification email",
    request=VerifyEmailSerializer,
)
@api_view(['POST'])
@permission_classes([AllowAny])
def verify_email(request):
    """
    Verify job seeker email address

    Activates user account and returns JWT tokens
    """
    serializer = VerifyEmailSerializer(data=request.data)

    if serializer.is_valid():
        user = serializer.user
        user.is_active = True
        user.email_verified = True
        user.activation_code = ''  # Clear the token
        user.save()

        # Generate JWT tokens
        tokens = get_tokens_for_user(user)

        return Response({
            "success": True,
            "user": UserSerializer(user).data,
            "access": tokens["access"],
            "refresh": tokens["refresh"],
            "message": "Email verified successfully"
        }, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=["Authentication"],
    summary="Resend Verification Email",
    description="Resend verification email to unverified job seeker",
    request=ResendVerificationSerializer,
)
@api_view(['POST'])
@permission_classes([AllowAny])
def resend_verification(request):
    """
    Resend verification email

    Generates new verification token and sends email
    """
    serializer = ResendVerificationSerializer(data=request.data)

    if serializer.is_valid():
        user = serializer.user

        # Generate new activation code
        user.activation_code = get_random_string(32)
        user.save()

        # Send verification email
        try:
            send_verification_email(user, request)
        except Exception:
            return Response({
                "success": False,
                "message": "Failed to send verification email. Please try again."
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({
            "success": True,
            "message": "Verification email sent successfully"
        }, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=["Authentication"],
    summary="Forgot Password",
    description="Request password reset email for job seeker",
    request=ForgotPasswordSerializer,
)
@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password(request):
    """
    Request password reset

    Sends password reset email if user exists
    """
    serializer = ForgotPasswordSerializer(data=request.data)

    if serializer.is_valid():
        # Check if user was found
        if hasattr(serializer, 'user'):
            user = serializer.user

            # Generate new reset token
            user.activation_code = get_random_string(32)
            user.save()

            # Send reset email
            try:
                send_password_reset_email(user, request)
            except Exception as e:
                print(f"Failed to send password reset email: {e}")

        # Always return success to prevent email enumeration
        return Response({
            "success": True,
            "message": "If an account with that email exists, you will receive a password reset link."
        }, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=["Authentication"],
    summary="Reset Password",
    description="Reset password using token from email",
    request=ResetPasswordSerializer,
)
@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password(request):
    """
    Reset password with token

    Updates password and clears reset token
    """
    serializer = ResetPasswordSerializer(data=request.data)

    if serializer.is_valid():
        user = serializer.user
        user.set_password(serializer.validated_data['password'])
        user.activation_code = ''  # Clear the token
        user.save()

        return Response({
            "success": True,
            "message": "Password reset successfully. You can now login with your new password."
        }, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
        "user": UserSerializer(user).data,
        "access": tokens["access"],
        "refresh": tokens["refresh"],
        "requires_profile_completion": requires_profile_completion,
        "redirect_to": redirect_to,
        "is_new_user": created,
    }

    return Response(response_data, status=status.HTTP_200_OK)


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

        # Get refresh token from cookie or request body (backward compatibility)
        refresh_token = request.COOKIES.get("refresh_token") or request.data.get("refresh")

        # Try to blacklist token if available
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except Exception as blacklist_error:
                # Log but don't fail - token might already be invalid
                print(f"Token blacklist error (continuing): {blacklist_error}")

        # Always clear cookies and return success (even if token missing/invalid)
        # This ensures user can logout even if token is corrupted
        response = Response(
            {"message": "Logout successful"}, status=status.HTTP_200_OK
        )

        # Get cookie domain for consistent clearing
        cookie_domain = getattr(settings, 'SESSION_COOKIE_DOMAIN', None)

        # Clear access token cookie
        response.delete_cookie(
            key='access_token',
            path='/',
            domain=cookie_domain,
            samesite='Lax',
        )

        # Clear refresh token cookie
        response.delete_cookie(
            key='refresh_token',
            path='/',
            domain=cookie_domain,
            samesite='Lax',
        )

        return response
    except Exception as e:
        # Even on error, try to clear cookies
        response = Response(
            {"message": "Logout completed (with errors)", "detail": str(e)},
            status=status.HTTP_200_OK  # Return 200 so frontend can continue
        )

        cookie_domain = getattr(settings, 'SESSION_COOKIE_DOMAIN', None)
        response.delete_cookie(key='access_token', path='/', domain=cookie_domain, samesite='Lax')
        response.delete_cookie(key='refresh_token', path='/', domain=cookie_domain, samesite='Lax')

        return response


@extend_schema(
    tags=["Authentication"],
    summary="Change Password",
    description="Change password for authenticated Job Seeker. Requires current password verification.",
    request=ChangePasswordSerializer,
    responses={
        200: {
            "type": "object",
            "properties": {"message": {"type": "string"}},
        },
        400: {
            "type": "object",
            "properties": {"error": {"type": "object"}},
        },
    },
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def change_password(request):
    """
    Change password for authenticated Job Seeker

    **Headers:**
    ```
    Authorization: Bearer <access_token>
    ```

    **Request Body:**
    ```json
    {
        "old_password": "current_password",
        "new_password": "new_password_here",
        "confirm_password": "new_password_here"
    }
    ```

    **Response (Success):**
    ```json
    {
        "message": "Password changed successfully"
    }
    ```

    **Response (Error):**
    ```json
    {
        "error": {
            "old_password": ["Current password is incorrect"]
        }
    }
    ```
    """
    serializer = ChangePasswordSerializer(
        data=request.data,
        context={'request': request}
    )

    if serializer.is_valid():
        # Set new password
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()

        return Response(
            {"message": "Password changed successfully"},
            status=status.HTTP_200_OK
        )

    return Response(
        {"error": serializer.errors},
        status=status.HTTP_400_BAD_REQUEST
    )


class CookieTokenRefreshView(TokenRefreshView):
    """
    Custom TokenRefreshView that reads refresh token from HttpOnly cookie
    and sets new tokens in HttpOnly cookies
    """
    def post(self, request, *args, **kwargs):
        # Get refresh token from cookie or request body (backward compatibility)
        refresh_token = request.COOKIES.get('refresh_token') or request.data.get('refresh')

        if not refresh_token:
            return Response(
                {"error": "Refresh token is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create request data with refresh token
        # Handle both QueryDict (from forms) and dict (from JSON)
        if hasattr(request.data, '_mutable'):
            # It's a QueryDict
            request.data._mutable = True
            request.data['refresh'] = refresh_token
            request.data._mutable = False
        else:
            # It's a regular dict, create a new mutable copy
            request._full_data = {'refresh': refresh_token}

        # Call parent class to perform token refresh
        try:
            response = super().post(request, *args, **kwargs)

            if response.status_code == 200:
                # Extract new tokens from response
                access_token = response.data.get('access')
                new_refresh_token = response.data.get('refresh', refresh_token)

                # Create new response without tokens in body
                new_response = Response(
                    {"message": "Token refreshed successfully"},
                    status=status.HTTP_200_OK
                )

                # Get cookie domain for cross-subdomain support
                cookie_domain = getattr(settings, 'SESSION_COOKIE_DOMAIN', None)

                # Set new access token cookie
                new_response.set_cookie(
                    key='access_token',
                    value=access_token,
                    max_age=7 * 24 * 60 * 60,  # 7 days
                    httponly=True,
                    secure=not settings.DEBUG,
                    samesite='Lax',
                    domain=cookie_domain,
                    path='/',
                )

                # Set new refresh token cookie
                new_response.set_cookie(
                    key='refresh_token',
                    value=new_refresh_token,
                    max_age=30 * 24 * 60 * 60,  # 30 days
                    httponly=True,
                    secure=not settings.DEBUG,
                    samesite='Lax',
                    domain=cookie_domain,
                    path='/',
                )

                return new_response

            return response

        except (TokenError, InvalidToken) as e:
            return Response(
                {"error": "Invalid or expired refresh token", "detail": str(e)},
                status=status.HTTP_401_UNAUTHORIZED
            )
