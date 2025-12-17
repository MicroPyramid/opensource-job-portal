"""
Authentication Utilities for Job Seekers
"""
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken
from peeldb.models import User, UserEmail, Google


def get_tokens_for_user(user):
    """
    Generate JWT tokens for user

    Args:
        user: User instance

    Returns:
        dict: Contains 'access' and 'refresh' tokens
    """
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


def create_or_update_google_user(user_document):
    """
    Create or update Job Seeker user from Google OAuth data

    Args:
        user_document (dict): Google user info dict containing:
            - email: User's email
            - id: Google user ID
            - given_name: First name
            - family_name: Last name
            - picture: Profile picture URL
            - verified_email: Email verification status
            - gender: Gender (optional)

    Returns:
        tuple: (user, created) where user is User instance and created is boolean

    Raises:
        ValueError: If email is not provided by Google
    """
    email = user_document.get("email", "")
    google_id = user_document.get("id", "")

    if not email:
        raise ValueError("Email not provided by Google")

    # Check if user exists by email
    email_match = UserEmail.objects.filter(email__iexact=email).first()

    if email_match:
        user = email_match.user
        created = False

        # Update user info if needed
        if not user.first_name:
            user.first_name = user_document.get("given_name", "")
        if not user.last_name:
            user.last_name = user_document.get("family_name", "")
        if not user.photo:
            user.photo = user_document.get("picture", "")
        if not user.profile_pic:
            user.profile_pic = user_document.get("picture", "")

        # Ensure user_type is Job Seeker for OAuth logins
        if user.user_type != "JS":
            user.user_type = "JS"

        user.is_active = True
        user.profile_updated = timezone.now()
        user.save()
    else:
        # Check if User exists without UserEmail record
        user = User.objects.filter(email__iexact=email).first()

        if user:
            created = False
            user.first_name = user_document.get("given_name", "")
            user.last_name = user_document.get("family_name", "")
            user.photo = user_document.get("picture", "")
            user.profile_pic = user_document.get("picture", "")
            user.profile_updated = timezone.now()
            user.is_active = True

            # Ensure user_type is Job Seeker for OAuth logins
            if user.user_type != "JS":
                user.user_type = "JS"

            user.save()
        else:
            # Create new Job Seeker user
            created = True
            user = User.objects.create(
                username=email,
                email=email,
                first_name=user_document.get("given_name", ""),
                last_name=user_document.get("family_name", ""),
                photo=user_document.get("picture", ""),
                profile_pic=user_document.get("picture", ""),
                user_type="JS",  # Job Seeker only
                profile_updated=timezone.now(),
                is_active=True,
                registered_from="Social",
            )

        # Create UserEmail record
        UserEmail.objects.get_or_create(
            user=user, email=email, defaults={"is_primary": True}
        )

    # Handle gender mapping
    if user_document.get("gender"):
        user.gender = "M" if user_document.get("gender") == "male" else "F"
        user.save()

    # Create or update Google record
    google_link = user_document.get("link", f"https://plus.google.com/{google_id}")

    google, _ = Google.objects.update_or_create(
        user=user,
        defaults={
            "google_url": google_link,
            "verified_email": user_document.get("verified_email", True),
            "google_id": google_id,
            "family_name": user_document.get("family_name", ""),
            "name": user_document.get("name", ""),
            "given_name": user_document.get("given_name", ""),
            "email": email,
            "picture": user_document.get("picture", ""),
        },
    )

    return user, created
