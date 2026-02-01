"""
Social Authentication Views
Only Google OAuth is supported.
"""
import requests

from django.shortcuts import render
from django.http.response import HttpResponseRedirect
from django.contrib.auth import login
from django.urls import reverse
from django.conf import settings

from peeldb.models import User, Google, UserEmail


def google_login(request):
    """
    Google OAuth login - for admin/staff and recruiters only.
    Job seeker login is handled by the SvelteKit frontend API.
    """
    if "code" in request.GET:
        params = {
            "grant_type": "authorization_code",
            "code": request.GET.get("code"),
            "redirect_uri": settings.GOOGLE_LOGIN_HOST + reverse("social:google_login"),
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
        }
        info = requests.post("https://accounts.google.com/o/oauth2/token", data=params)
        info = info.json()

        if not info.get("access_token"):
            return render(
                request,
                "404.html",
                {
                    "message": "Sorry, Your session has been expired",
                    "reason": "Please kindly try again to update your profile",
                    "email": settings.DEFAULT_FROM_EMAIL,
                },
                status=404,
            )

        url = "https://www.googleapis.com/oauth2/v1/userinfo"
        params = {"access_token": info["access_token"]}
        response = requests.get(url, params=params, timeout=60)
        user_document = response.json()

        email = user_document.get("email", "")
        if not email:
            return render(
                request,
                "404.html",
                {
                    "message": "Could not retrieve email",
                    "reason": "Please try again",
                    "email": settings.DEFAULT_FROM_EMAIL,
                },
                status=404,
            )

        link = user_document.get("link", f"https://plus.google.com/{user_document.get('id', '')}")
        picture = user_document.get("picture", "")
        dob = user_document.get("birthday", "")
        gender = user_document.get("gender", "")

        # Find user by email
        email_match = UserEmail.objects.filter(email__iexact=email).first()
        if email_match:
            user = email_match.user
        else:
            user = User.objects.filter(email__iexact=email).first()

        if not user:
            # No user found - don't create new users via this endpoint
            return render(
                request,
                "404.html",
                {
                    "message": "Account not found",
                    "reason": "No account exists with this email. Please contact an administrator.",
                    "email": settings.DEFAULT_FROM_EMAIL,
                },
                status=404,
            )

        # Update/create Google record
        Google.objects.get_or_create(
            user=user,
            defaults={
                'google_url': link,
                'verified_email': user_document.get("verified_email", ""),
                'google_id': user_document.get("id", ""),
                'family_name': user_document.get("family_name", ""),
                'name': user_document.get("name", ""),
                'given_name': user_document.get("given_name", ""),
                'dob': dob,
                'email': email,
                'gender': gender,
                'picture': picture,
            }
        )

        # Ensure UserEmail exists
        UserEmail.objects.get_or_create(
            user=user,
            email=email,
            defaults={'is_primary': True}
        )

        user.is_active = True
        user.save()
        login(request, user, backend="django.contrib.auth.backends.ModelBackend")

        # Redirect based on user type
        if user.is_superuser or user.is_staff:
            return HttpResponseRedirect("/dashboard/")

        if user.is_recruiter or user.is_agency_recruiter:
            recruiter_url = getattr(settings, 'RECRUITER_FRONTEND_URL', 'http://localhost:5174')
            return HttpResponseRedirect(f"{recruiter_url}/dashboard")

        # Job seekers should use the frontend API, not this endpoint
        return render(
            request,
            "404.html",
            {
                "message": "Access denied",
                "reason": "This login is only for administrators and recruiters.",
                "email": settings.DEFAULT_FROM_EMAIL,
            },
            status=403,
        )

    else:
        # Redirect to Google OAuth
        oauth_url = (
            "https://accounts.google.com/o/oauth2/auth"
            f"?client_id={settings.GOOGLE_CLIENT_ID}"
            "&response_type=code"
            "&scope=https://www.googleapis.com/auth/userinfo.profile "
            "https://www.googleapis.com/auth/userinfo.email"
            f"&redirect_uri={settings.GOOGLE_LOGIN_HOST}{reverse('social:google_login')}"
            "&state=1235dfghjkf123"
        )
        return HttpResponseRedirect(oauth_url)
