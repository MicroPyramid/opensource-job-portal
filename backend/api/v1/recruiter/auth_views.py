"""
Authentication Views for Recruiter/Employer
"""

import requests
from django.conf import settings
from django.core import signing
from django.utils.crypto import get_random_string
from drf_spectacular.utils import PolymorphicProxySerializer, extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from peeldb.models import Company, Google, User

from ..common.responses import (
    VALIDATION_ERROR_RESPONSE,
    ErrorResponseSerializer,
    SuccessMessageResponseSerializer,
)
from .auth_serializers import (
    ChangePasswordSerializer,
    ForgotPasswordSerializer,
    GoogleAuthUrlSerializer,
    GoogleCallbackSerializer,
    GoogleCompleteSerializer,
    LoginSerializer,
    RecruiterAuthTokenResponseSerializer,
    RecruiterGoogleAdditionalInfoSerializer,
    RecruiterGoogleAuthenticatedSerializer,
    RecruiterGoogleAuthUrlResponseSerializer,
    RecruiterGoogleCompleteResponseSerializer,
    RecruiterLoginResponseSerializer,
    RecruiterProfilePictureUploadSerializer,
    RecruiterProfileUpdateResponseSerializer,
    RecruiterRegisterResponseSerializer,
    RegisterSerializer,
    ResendVerificationSerializer,
    ResetPasswordSerializer,
    UpdateProfileSerializer,
    UserSerializer,
    VerifyEmailSerializer,
)
from .serializers import AcceptInvitationSerializer

# Namespaces the signature so a blob from this flow cannot be replayed against
# any other signed payload in the project.
GOOGLE_SIGNUP_SALT = "api.v1.recruiter.google-signup"

# How long a half-finished Google signup stays valid. Long enough to fill in
# the company form, short enough that a leaked URL goes stale quickly.
GOOGLE_SIGNUP_MAX_AGE = 30 * 60


def get_tokens_for_user(user):
    """Generate JWT tokens for user"""
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


def send_verification_email(user, request, company=None):
    """Send email verification link"""
    from datetime import datetime

    from django.template import loader

    from dashboard.tasks import send_email

    # Use recruiter UI URL for verification
    frontend_url = (
        settings.RECRUITER_FRONTEND_URL
        if hasattr(settings, "RECRUITER_FRONTEND_URL")
        else "http://localhost:5174"
    )
    verification_url = f"{frontend_url}/verify-email?token={user.activation_code}"

    # Render email template
    template = loader.get_template("recruiter/email/verification.html")
    context = {
        "user": user,
        "company": company,
        "verification_url": verification_url,
        "current_year": datetime.now().year,
    }
    html_content = template.render(context)

    # Send email - use .delay() for Celery async, or direct call for sync
    if settings.DEBUG:
        # Synchronous email for development (no Celery needed)
        send_email(
            mto=[user.email],
            msubject="Verify your PeelJobs Recruiter account",
            mbody=html_content,
        )
    else:
        # Async email via Celery for production
        send_email.delay(
            mto=[user.email],
            msubject="Verify your PeelJobs Recruiter account",
            mbody=html_content,
        )


def send_password_reset_email(user, request):
    """Send password reset link"""
    from datetime import datetime

    from django.template import loader

    from dashboard.tasks import send_email

    # Use recruiter UI URL for password reset
    frontend_url = (
        settings.RECRUITER_FRONTEND_URL
        if hasattr(settings, "RECRUITER_FRONTEND_URL")
        else "http://localhost:5174"
    )
    reset_url = f"{frontend_url}/reset-password?token={user.activation_code}"

    # Render email template
    template = loader.get_template("recruiter/email/password_reset.html")
    context = {
        "user": user,
        "reset_url": reset_url,
        "current_year": datetime.now().year,
    }
    html_content = template.render(context)

    # Send email - use .delay() for Celery async, or direct call for sync
    if settings.DEBUG:
        # Synchronous email for development (no Celery needed)
        send_email(
            mto=[user.email],
            msubject="Reset your PeelJobs Recruiter password",
            mbody=html_content,
        )
    else:
        # Async email via Celery for production
        send_email.delay(
            mto=[user.email],
            msubject="Reset your PeelJobs Recruiter password",
            mbody=html_content,
        )


@extend_schema(
    tags=["Recruiter Auth"],
    summary="Register New Recruiter/Company",
    description="Create new recruiter or company account",
    request=RegisterSerializer,
    responses={
        201: RecruiterRegisterResponseSerializer,
        400: VALIDATION_ERROR_RESPONSE,
    },
)
@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    """
    Register new recruiter or company account

    Creates user and optionally company, sends verification email
    """
    serializer = RegisterSerializer(data=request.data)

    if serializer.is_valid():
        result = serializer.save()
        user = result["user"]
        company = result["company"]

        # Send verification email
        send_verification_email(user, request, company)

        return Response(
            {
                "success": True,
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "user_type": user.user_type,
                    "is_active": user.is_active,
                },
                "company": {
                    "id": company.id,
                    "name": company.name,
                    "slug": company.slug,
                }
                if company
                else None,
                "message": "Registration successful. Please check your email to verify your account.",
            },
            status=status.HTTP_201_CREATED,
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=["Recruiter Auth"],
    summary="Login",
    description="Authenticate recruiter/company user",
    request=LoginSerializer,
    responses={
        200: RecruiterLoginResponseSerializer,
        400: VALIDATION_ERROR_RESPONSE,
    },
)
@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    """
    Login for recruiter/company users

    Returns JWT tokens in response body ONLY (not in cookies)
    SvelteKit frontend will store these in HttpOnly cookies
    """
    serializer = LoginSerializer(data=request.data)

    if serializer.is_valid():
        user = serializer.validated_data["user"]

        # Generate tokens
        tokens = get_tokens_for_user(user)

        # Get user data
        user_serializer = UserSerializer(user)

        # Return JWT tokens in response body ONLY
        # SvelteKit will store these in HttpOnly cookies via /api/auth/set-cookies
        return Response(
            {
                "access": tokens["access"],
                "refresh": tokens["refresh"],
                "user": user_serializer.data,
            }
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=["Recruiter Auth"],
    summary="Logout",
    description="Logout and clear tokens",
    # No body is read; the view unconditionally returns success. Cookie
    # clearing is SvelteKit's job, not Django's.
    request=None,
    responses={200: SuccessMessageResponseSerializer},
)
@api_view(["POST"])
@permission_classes([AllowAny])
def logout(request):
    """
    Logout user

    Django does NOT manage cookies - SvelteKit handles cookie clearing
    This endpoint is just for blacklisting tokens if needed
    """
    return Response({"success": True, "message": "Logged out successfully"})


@extend_schema(
    tags=["Recruiter Auth"],
    summary="Verify Email",
    description="Verify email address with token",
    request=VerifyEmailSerializer,
    responses={
        200: RecruiterAuthTokenResponseSerializer,
        400: VALIDATION_ERROR_RESPONSE,
    },
)
@api_view(["POST"])
@permission_classes([AllowAny])
def verify_email(request):
    """
    Verify email address

    Activates account and auto-logs in user
    Returns JWT tokens in response body (SvelteKit stores in cookies)
    """
    serializer = VerifyEmailSerializer(data=request.data)

    if serializer.is_valid():
        user = serializer.context["user"]

        # Activate user
        user.is_active = True
        user.email_verified = True
        user.save()

        # Auto-login - generate tokens
        tokens = get_tokens_for_user(user)
        user_serializer = UserSerializer(user)

        # Return tokens in response body ONLY (not in cookies)
        return Response(
            {
                "success": True,
                "access": tokens["access"],
                "refresh": tokens["refresh"],
                "user": user_serializer.data,
                "message": "Email verified successfully",
            }
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=["Recruiter Auth"],
    summary="Resend Verification Email",
    description="Resend email verification link",
    request=ResendVerificationSerializer,
    responses={
        # Success is returned whether or not the account exists, to avoid
        # leaking which addresses are registered.
        200: SuccessMessageResponseSerializer,
        400: VALIDATION_ERROR_RESPONSE,
    },
)
@api_view(["POST"])
@permission_classes([AllowAny])
def resend_verification(request):
    """Resend verification email"""
    serializer = ResendVerificationSerializer(data=request.data)

    if serializer.is_valid():
        user = serializer.context.get("user")

        if user:
            send_verification_email(user, request)

        # Always return success (don't reveal if email exists)
        return Response(
            {
                "success": True,
                "message": "If an account exists with this email, you will receive verification instructions",
            }
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=["Recruiter Auth"],
    summary="Forgot Password",
    description="Request password reset link",
    request=ForgotPasswordSerializer,
    responses={
        200: SuccessMessageResponseSerializer,
        400: VALIDATION_ERROR_RESPONSE,
    },
)
@api_view(["POST"])
@permission_classes([AllowAny])
def forgot_password(request):
    """Request password reset"""
    serializer = ForgotPasswordSerializer(data=request.data)

    if serializer.is_valid():
        user = serializer.context.get("user")

        if user:
            # Generate new activation code for password reset
            user.activation_code = get_random_string(32)
            user.save()

            send_password_reset_email(user, request)

        # Always return success (security)
        return Response(
            {
                "success": True,
                "message": "If an account exists with this email, you will receive password reset instructions",
            }
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=["Recruiter Auth"],
    summary="Reset Password",
    description="Reset password with token",
    request=ResetPasswordSerializer,
    responses={
        200: SuccessMessageResponseSerializer,
        400: VALIDATION_ERROR_RESPONSE,
    },
)
@api_view(["POST"])
@permission_classes([AllowAny])
def reset_password(request):
    """Reset password with token"""
    serializer = ResetPasswordSerializer(data=request.data)

    if serializer.is_valid():
        user = serializer.context["user"]

        # Update password
        user.set_password(serializer.validated_data["password"])
        # Clear activation code (one-time use)
        user.activation_code = ""
        user.save()

        return Response({"success": True, "message": "Password reset successfully"})

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=["Recruiter Auth"],
    summary="Change Password",
    description="Change password for authenticated user",
    request=ChangePasswordSerializer,
    responses={
        200: SuccessMessageResponseSerializer,
        400: VALIDATION_ERROR_RESPONSE,
    },
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def change_password(request):
    """Change password for authenticated user"""
    serializer = ChangePasswordSerializer(
        data=request.data, context={"request": request}
    )

    if serializer.is_valid():
        user = request.user
        user.set_password(serializer.validated_data["new_password"])
        user.save()

        return Response({"success": True, "message": "Password changed successfully"})

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=["Recruiter Auth"],
    summary="Get Current User",
    description="Get authenticated user info",
    responses={200: UserSerializer},
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me(request):
    """Get current user info"""
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


@extend_schema(
    tags=["Recruiter Auth"],
    summary="Accept Team Invitation",
    description="Accept team invitation during signup",
    request=AcceptInvitationSerializer,
    responses={
        201: RecruiterAuthTokenResponseSerializer,
        400: VALIDATION_ERROR_RESPONSE,
    },
)
@api_view(["POST"])
@permission_classes([AllowAny])
def accept_invitation(request):
    """
    Accept team invitation

    Creates user account linked to company from invitation
    """
    serializer = AcceptInvitationSerializer(
        data=request.data, context={"request": request}
    )

    if serializer.is_valid():
        user = serializer.save()

        # Auto-login
        tokens = get_tokens_for_user(user)
        user_serializer = UserSerializer(user)

        response = Response(
            {
                "success": True,
                "access": tokens["access"],
                "refresh": tokens["refresh"],
                "user": user_serializer.data,
                "message": f"Account created successfully. Welcome to {user.company.name}!",
            },
            status=status.HTTP_201_CREATED,
        )

        # Return tokens in response body only (no cookies)
        return response

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Google OAuth Views
@extend_schema(
    tags=["Recruiter Auth - OAuth"],
    summary="Get Google OAuth URL",
    description="Generate Google OAuth authorization URL",
    parameters=[GoogleAuthUrlSerializer],
    responses={
        200: RecruiterGoogleAuthUrlResponseSerializer,
        400: VALIDATION_ERROR_RESPONSE,
    },
)
@api_view(["GET"])
@permission_classes([AllowAny])
def google_auth_url(request):
    """Get Google OAuth URL for recruiters"""
    serializer = GoogleAuthUrlSerializer(data=request.query_params)

    if serializer.is_valid():
        redirect_uri = serializer.validated_data["redirect_uri"]
        account_type = serializer.validated_data["account_type"]

        # Build Google OAuth URL
        google_auth_url = (
            "https://accounts.google.com/o/oauth2/auth"
            f"?client_id={settings.GOOGLE_CLIENT_ID}"
            "&response_type=code"
            "&scope=https://www.googleapis.com/auth/userinfo.profile "
            "https://www.googleapis.com/auth/userinfo.email"
            f"&redirect_uri={redirect_uri}"
            f"&state={account_type}"  # company or recruiter
            "&access_type=offline"
            "&prompt=consent"
        )

        return Response({"auth_url": google_auth_url, "account_type": account_type})

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=["Recruiter Auth - OAuth"],
    summary="Google OAuth Callback",
    description="Handle Google OAuth callback",
    request=GoogleCallbackSerializer,
    responses={
        # Two distinct 200 bodies, discriminated by `status`: an already-linked
        # Google account logs straight in, an unknown one asks the client to
        # finish signing up.
        200: PolymorphicProxySerializer(
            component_name="RecruiterGoogleCallbackResponse",
            serializers={
                "authenticated": RecruiterGoogleAuthenticatedSerializer,
                "additional_info_required": RecruiterGoogleAdditionalInfoSerializer,
            },
            resource_type_field_name="status",
        ),
        400: ErrorResponseSerializer,
        500: ErrorResponseSerializer,
    },
)
@api_view(["POST"])
@permission_classes([AllowAny])
def google_callback(request):
    """
    Handle Google OAuth callback

    Either auto-logs in existing user or returns Google data for registration
    """
    serializer = GoogleCallbackSerializer(data=request.data)

    if serializer.is_valid():
        code = serializer.validated_data["code"]
        redirect_uri = serializer.validated_data["redirect_uri"]

        try:
            # Exchange code for tokens
            token_response = requests.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "code": code,
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "redirect_uri": redirect_uri,
                    "grant_type": "authorization_code",
                },
            )
            token_data = token_response.json()

            if "error" in token_data:
                return Response(
                    {"error": token_data.get("error_description", "OAuth error")},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Get user info from Google
            user_info_response = requests.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {token_data['access_token']}"},
            )
            google_data = user_info_response.json()

            # Check if Google account already linked
            try:
                google_obj = Google.objects.get(google_id=google_data["id"])
                user = google_obj.user

                # Check if user is employer type
                if user.user_type != "EM":
                    return Response(
                        {
                            "error": "This Google account is linked to a job seeker account"
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                # Existing user - auto login
                tokens = get_tokens_for_user(user)
                user_serializer = UserSerializer(user)

                # Return tokens in response body ONLY (no cookies)
                # SvelteKit will store these in HttpOnly cookies
                return Response(
                    {
                        "status": "authenticated",
                        "access": tokens["access"],
                        "refresh": tokens["refresh"],
                        "user": user_serializer.data,
                    }
                )

            except Google.DoesNotExist:
                # New user — hand the verified Google identity back to the
                # client so it can be replayed to google_complete.
                #
                # This used to be stashed in ``request.session``. That could
                # never work: the only caller is the SvelteKit server, which
                # talks to us machine-to-machine and keeps no session cookie,
                # so every request built a fresh empty session and
                # google_complete always answered "Invalid or expired session
                # token". A cache would work but adds a shared-state
                # dependency (CACHES is unset, so it is per-process LocMem —
                # wrong the moment there is more than one worker).
                #
                # Signing instead keeps it stateless: the blob is tamper-proof
                # via SECRET_KEY, so google_complete can trust the identity it
                # reads back without having stored anything. The client cannot
                # forge an email or google_id.
                session_token = signing.dumps(
                    {
                        "google_id": google_data["id"],
                        "email": google_data["email"],
                        "first_name": google_data.get("given_name", ""),
                        "last_name": google_data.get("family_name", ""),
                        "picture": google_data.get("picture", ""),
                    },
                    salt=GOOGLE_SIGNUP_SALT,
                )

                return Response(
                    {
                        "status": "additional_info_required",
                        "google_data": {
                            "email": google_data["email"],
                            "first_name": google_data.get("given_name", ""),
                            "last_name": google_data.get("family_name", ""),
                            "picture": google_data.get("picture", ""),
                        },
                        "session_token": session_token,
                    }
                )

        except Exception as e:
            return Response(
                {"error": f"OAuth error: {e!s}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=["Recruiter Auth - OAuth"],
    summary="Complete Google OAuth Registration",
    description="Complete registration with additional info",
    request=GoogleCompleteSerializer,
    responses={
        201: RecruiterGoogleCompleteResponseSerializer,
        400: ErrorResponseSerializer,
    },
)
@api_view(["POST"])
@permission_classes([AllowAny])
def google_complete(request):
    """Complete Google OAuth registration with additional info"""
    serializer = GoogleCompleteSerializer(data=request.data)

    if serializer.is_valid():
        session_token = serializer.validated_data["session_token"]

        # Unseal the identity google_callback signed. A bad signature means
        # the payload was edited; SignatureExpired means the user sat on the
        # signup form past the window. Both are the same answer to the client.
        try:
            google_session_data = signing.loads(
                session_token,
                salt=GOOGLE_SIGNUP_SALT,
                max_age=GOOGLE_SIGNUP_MAX_AGE,
            )
        except signing.BadSignature:
            return Response(
                {"error": "Invalid or expired session token"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create user similar to regular registration
        from django.template.defaultfilters import slugify

        account_type = serializer.validated_data["account_type"]
        email = google_session_data["email"]

        # Check if email already exists
        if User.objects.filter(email=email).exists():
            return Response(
                {"error": "A user with this email already exists"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create company if needed
        company = None
        if account_type == "company":
            company_slug = slugify(serializer.validated_data["company_name"])
            base_slug = company_slug
            counter = 1
            while Company.objects.filter(slug=company_slug).exists():
                company_slug = f"{base_slug}-{counter}"
                counter += 1

            company = Company.objects.create(
                name=serializer.validated_data["company_name"],
                website=serializer.validated_data.get("company_website", ""),
                size=serializer.validated_data.get("company_size", ""),
                company_type="Company",
                slug=company_slug,
                profile="",
                address="",
                phone_number=serializer.validated_data.get("phone", ""),
                email=email,
                is_active=True,
            )

        # Create user
        username = email.split("@")[0] + "_" + get_random_string(6)
        user = User.objects.create(
            username=username,
            email=email,
            first_name=google_session_data["first_name"],
            last_name=google_session_data["last_name"],
            user_type="EM",
            company=company,
            is_admin=account_type == "company",
            job_title=serializer.validated_data.get("job_title", ""),
            mobile=serializer.validated_data.get("phone", ""),
            is_active=True,  # Pre-verified via Google
            email_verified=True,
        )

        # Link Google account
        Google.objects.create(
            user=user,
            google_id=google_session_data["google_id"],
            google_url=google_session_data.get("picture", ""),
            verified_email=True,
            family_name=google_session_data.get("last_name", ""),
            given_name=google_session_data.get("first_name", ""),
            email=email,
            picture=google_session_data.get("picture", ""),
        )

        # Nothing to clear — the token is stateless. It stays replayable until
        # it expires, but the duplicate-email check above already makes a
        # second use a no-op.

        # Auto-login
        tokens = get_tokens_for_user(user)
        user_serializer = UserSerializer(user)

        # Return tokens in response body ONLY (no cookies)
        # SvelteKit will store these in HttpOnly cookies
        return Response(
            {
                "success": True,
                "access": tokens["access"],
                "refresh": tokens["refresh"],
                "user": user_serializer.data,
                "company": {
                    "id": company.id,
                    "name": company.name,
                    "slug": company.slug,
                }
                if company
                else None,
            },
            status=status.HTTP_201_CREATED,
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Profile Management Views
@extend_schema(
    tags=["Recruiter Profile"],
    summary="Update Profile",
    description="Update recruiter profile information",
    request=UpdateProfileSerializer,
    responses={
        200: RecruiterProfileUpdateResponseSerializer,
        400: VALIDATION_ERROR_RESPONSE,
    },
)
@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def update_profile(request):
    """
    Update recruiter profile

    Allows updating: first_name, last_name, job_title, mobile
    """
    serializer = UpdateProfileSerializer(data=request.data, instance=request.user)

    if serializer.is_valid():
        user = serializer.save()

        # Return updated user data
        user_serializer = UserSerializer(user)

        return Response(
            {
                "success": True,
                "user": user_serializer.data,
                "message": "Profile updated successfully",
            }
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=["Recruiter Profile"],
    summary="Upload Profile Picture",
    description="Upload or update profile picture",
    request=RecruiterProfilePictureUploadSerializer,
    responses={
        200: RecruiterProfileUpdateResponseSerializer,
        # Missing file, wrong content type, or over 2MB — all single-key errors.
        400: ErrorResponseSerializer,
    },
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def upload_profile_picture(request):
    """
    Upload profile picture

    Accepts multipart/form-data with 'profile_pic' field
    """
    if "profile_pic" not in request.FILES:
        return Response(
            {"error": "Please provide a profile_pic file"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    profile_pic = request.FILES["profile_pic"]

    # Validate file type
    allowed_types = ["image/jpeg", "image/jpg", "image/png"]
    if profile_pic.content_type not in allowed_types:
        return Response(
            {"error": "Invalid file type. Please upload a JPEG or PNG image"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Validate file size (max 2MB)
    max_size = 2 * 1024 * 1024  # 2MB
    if profile_pic.size > max_size:
        return Response(
            {"error": "File too large. Maximum size is 2MB"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Save profile picture
    user = request.user
    user.profile_pic = profile_pic
    user.save()

    # Return updated user data
    user_serializer = UserSerializer(user)

    return Response(
        {
            "success": True,
            "user": user_serializer.data,
            "message": "Profile picture uploaded successfully",
        }
    )
