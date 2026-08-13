"""
Tests for Job Seeker Google Authentication API
"""

from unittest.mock import MagicMock, patch

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from peeldb.models import Google, User, UserEmail


class GoogleAuthAPITests(TestCase):
    """Test suite for Google OAuth authentication for Job Seekers"""

    def setUp(self):
        """Set up test client and test data"""
        self.client = APIClient()
        self.google_auth_url = reverse("api:v1:auth:google-auth-url")
        self.google_callback_url = reverse("api:v1:auth:google-callback")
        self.google_disconnect_url = reverse("api:v1:auth:google-disconnect")
        self.current_user_url = reverse("api:v1:auth:current-user")
        self.logout_url = reverse("api:v1:auth:logout")

    def test_google_auth_url_generation(self):
        """Test Google OAuth URL generation with valid redirect_uri"""
        response = self.client.get(
            self.google_auth_url,
            {"redirect_uri": "http://localhost:3000/auth/callback"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("auth_url", response.data)
        self.assertIn("accounts.google.com", response.data["auth_url"])
        self.assertEqual(response.data["user_type"], "JS")

    def test_google_auth_url_missing_redirect_uri(self):
        """Test Google OAuth URL generation without redirect_uri fails"""
        response = self.client.get(self.google_auth_url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch("requests.post")
    @patch("requests.get")
    def test_google_callback_new_user(self, mock_get, mock_post):
        """Test Google callback creates new Job Seeker user"""
        # Mock Google token exchange
        mock_post.return_value = MagicMock(
            json=lambda: {"access_token": "fake_access_token"},
            raise_for_status=lambda: None,
        )

        # Mock Google user info
        mock_get.return_value = MagicMock(
            json=lambda: {
                "email": "newuser@example.com",
                "id": "12345",
                "given_name": "John",
                "family_name": "Doe",
                "picture": "http://example.com/pic.jpg",
                "verified_email": True,
            },
            raise_for_status=lambda: None,
        )

        response = self.client.post(
            self.google_callback_url,
            {
                "code": "fake_auth_code",
                "redirect_uri": "http://localhost:3000/callback",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertIn("user", response.data)
        self.assertTrue(response.data["is_new_user"])

        # Verify user was created
        user = User.objects.get(email="newuser@example.com")
        self.assertEqual(user.first_name, "John")
        self.assertEqual(user.last_name, "Doe")
        self.assertEqual(user.user_type, "JS")  # Job Seeker

        # Verify Google record was created
        google = Google.objects.get(user=user)
        self.assertEqual(google.google_id, "12345")
        self.assertEqual(google.email, "newuser@example.com")

        # Verify UserEmail record was created
        user_email = UserEmail.objects.get(user=user)
        self.assertEqual(user_email.email, "newuser@example.com")
        self.assertTrue(user_email.is_primary)

    @patch("requests.post")
    @patch("requests.get")
    def test_google_callback_existing_user(self, mock_get, mock_post):
        """Test Google callback for existing user"""
        # Create existing user
        existing_user = User.objects.create(
            username="existing@example.com",
            email="existing@example.com",
            first_name="Jane",
            user_type="JS",
            is_active=True,
        )
        UserEmail.objects.create(
            user=existing_user, email="existing@example.com", is_primary=True
        )

        # Mock Google responses
        mock_post.return_value = MagicMock(
            json=lambda: {"access_token": "fake_access_token"},
            raise_for_status=lambda: None,
        )

        mock_get.return_value = MagicMock(
            json=lambda: {
                "email": "existing@example.com",
                "id": "67890",
                "given_name": "Jane",
                "family_name": "Smith",
                "picture": "http://example.com/pic2.jpg",
                "verified_email": True,
            },
            raise_for_status=lambda: None,
        )

        response = self.client.post(
            self.google_callback_url,
            {
                "code": "fake_auth_code",
                "redirect_uri": "http://localhost:3000/callback",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["is_new_user"])

        # Verify user was not duplicated
        self.assertEqual(User.objects.filter(email="existing@example.com").count(), 1)

        # Verify Google record was created
        google = Google.objects.get(user=existing_user)
        self.assertEqual(google.google_id, "67890")

    @patch("requests.post")
    def test_google_callback_invalid_code(self, mock_post):
        """Test Google callback with invalid code"""
        # Mock failed token exchange
        mock_post.side_effect = Exception("Invalid code")

        response = self.client.post(
            self.google_callback_url,
            {
                "code": "invalid_code",
                "redirect_uri": "http://localhost:3000/callback",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_current_user_authenticated(self):
        """Test getting current user info when authenticated"""
        # Create test user
        user = User.objects.create(
            username="testuser@example.com",
            email="testuser@example.com",
            first_name="Test",
            last_name="User",
            user_type="JS",
            is_active=True,
        )

        # Authenticate user
        self.client.force_authenticate(user=user)

        response = self.client.get(self.current_user_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "testuser@example.com")
        self.assertEqual(response.data["user_type"], "JS")

    def test_current_user_unauthenticated(self):
        """Test getting current user info when not authenticated"""
        response = self.client.get(self.current_user_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_google_disconnect_success(self):
        """Test disconnecting Google account"""
        # Create user with Google connection
        user = User.objects.create(
            username="testuser@example.com",
            email="testuser@example.com",
            user_type="JS",
            is_active=True,
        )
        Google.objects.create(
            user=user,
            google_id="12345",
            email="testuser@example.com",
            name="Test User",
        )

        # Authenticate user
        self.client.force_authenticate(user=user)

        response = self.client.post(self.google_disconnect_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("message", response.data)

        # Verify Google record was deleted
        self.assertFalse(Google.objects.filter(user=user).exists())

    def test_google_disconnect_no_connection(self):
        """Test disconnecting Google when no connection exists"""
        # Create user without Google connection
        user = User.objects.create(
            username="testuser@example.com",
            email="testuser@example.com",
            user_type="JS",
            is_active=True,
        )

        # Authenticate user
        self.client.force_authenticate(user=user)

        response = self.client.post(self.google_disconnect_url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("error", response.data)

    @patch("requests.post")
    @patch("requests.get")
    def test_profile_completion_redirect(self, mock_get, mock_post):
        """Test that new users with low profile completion are redirected to profile page"""
        # Mock Google responses
        mock_post.return_value = MagicMock(
            json=lambda: {"access_token": "fake_access_token"},
            raise_for_status=lambda: None,
        )

        mock_get.return_value = MagicMock(
            json=lambda: {
                "email": "incomplete@example.com",
                "id": "99999",
                "given_name": "Incomplete",
                "family_name": "User",
                "picture": "http://example.com/pic.jpg",
                "verified_email": True,
            },
            raise_for_status=lambda: None,
        )

        response = self.client.post(
            self.google_callback_url,
            {
                "code": "fake_auth_code",
                "redirect_uri": "http://localhost:3000/callback",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check if profile completion is required
        user = User.objects.get(email="incomplete@example.com")
        if user.profile_completion_percentage < 50:
            self.assertTrue(response.data["requires_profile_completion"])
            self.assertEqual(response.data["redirect_to"], "/profile/complete")
        else:
            self.assertFalse(response.data["requires_profile_completion"])
            self.assertEqual(response.data["redirect_to"], "/dashboard")


class LoginAPITests(TestCase):
    """Email + password login for job seekers."""

    def setUp(self):
        self.client = APIClient()
        self.login_url = reverse("api:v1:auth:login")
        self.current_user_url = reverse("api:v1:auth:current-user")

        self.password = "Str0ng!Passw0rd"
        self.user = User.objects.create_user(
            username="seeker@example.com",
            email="seeker@example.com",
            password=self.password,
        )
        self.user.user_type = "JS"
        self.user.is_active = True
        self.user.email_verified = True
        self.user.save()

    def _post(self, **payload):
        return self.client.post(self.login_url, payload, format="json")

    def test_login_returns_tokens(self):
        response = self._post(email=self.user.email, password=self.password)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertEqual(response.data["user"]["email"], self.user.email)

    def test_returned_access_token_authenticates(self):
        """The token is not just well-formed — it works on a protected route."""
        access = self._post(email=self.user.email, password=self.password).data[
            "access"
        ]

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = self.client.get(self.current_user_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], self.user.email)

    def test_email_is_case_insensitive(self):
        response = self._post(email="SEEKER@EXAMPLE.COM", password=self.password)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_wrong_password_rejected(self):
        response = self._post(email=self.user.email, password="wrong-password")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn("access", response.data)

    def test_unknown_email_rejected(self):
        response = self._post(email="nobody@example.com", password=self.password)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn("access", response.data)

    def test_blank_password_cannot_authenticate(self):
        """
        Regression guard for the PasswordlessAuthBackend bypass.

        That backend is first in AUTHENTICATION_BACKENDS and returns the user
        unchecked when handed a falsy password, so a blank password reaching
        authenticate() would be an account takeover.
        """
        for blank in ("", "   ", None):
            with self.subTest(password=blank):
                response = self._post(email=self.user.email, password=blank)
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertNotIn("access", response.data)

    def test_missing_password_field_rejected(self):
        response = self.client.post(
            self.login_url, {"email": self.user.email}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn("access", response.data)

    def test_unverified_account_rejected(self):
        self.user.is_active = False
        self.user.save()

        response = self._post(email=self.user.email, password=self.password)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("verify", str(response.data).lower())

    def test_employer_sent_to_recruiter_login(self):
        self.user.user_type = "EM"
        self.user.save()

        response = self._post(email=self.user.email, password=self.password)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("recruiter", str(response.data).lower())
