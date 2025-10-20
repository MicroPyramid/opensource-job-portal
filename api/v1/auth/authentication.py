"""
Custom JWT Authentication for HttpOnly Cookies
Extends djangorestframework-simplejwt to read tokens from cookies instead of headers
"""
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed


class CookieJWTAuthentication(JWTAuthentication):
    """
    Custom JWT authentication that reads access token from HttpOnly cookies
    Falls back to Authorization header for backward compatibility
    """

    def authenticate(self, request):
        # Try to get token from cookie first (preferred for security)
        raw_token = request.COOKIES.get('access_token')

        # Fall back to Authorization header if cookie not present
        if not raw_token:
            header = self.get_header(request)
            if header is None:
                return None

            raw_token = self.get_raw_token(header)

        if raw_token is None:
            return None

        # Validate token
        validated_token = self.get_validated_token(raw_token)

        # Return user and validated token
        return self.get_user(validated_token), validated_token
