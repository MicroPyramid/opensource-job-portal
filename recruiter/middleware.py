from django.shortcuts import redirect
from django.contrib.auth import logout
from django.conf import settings
# from administration.models import Company, Profile
from rest_framework.authtoken.models import Token
# from recruiter import status
from django.http.response import JsonResponse
# from microtrack.authentication import TokenAuthentication
from rest_framework.authentication import (
    BaseAuthentication, get_authorization_header
)

from recruiter import exceptions, status
from django.http import HttpResponseRedirect


class TokenAuthentication(BaseAuthentication):
    """
    Simple token based authentication.
    Clients should authenticate by passing the token key in the "Authorization"
    HTTP header, prepended with the string "Token ".  For example:
        Authorization: Token 401f7ac837da42b97f613d789819ff93537bee6a
    """

    keyword = 'Token'
    model = None

    def get_model(self):
        if self.model is not None:
            return self.model
        from rest_framework.authtoken.models import Token
        return Token

    """
    A custom token model may be used, but must have the following properties.
    * key -- The string identifying the token
    * user -- The user to which the token belongs
    """

    def authenticate(self, request):
        auth = get_authorization_header(request).split()

        if not auth or auth[0].lower() != self.keyword.lower().encode():
            return None

        if len(auth) == 1:
            raise exceptions.AuthenticationFailed(
                'Invalid token header. No credentials provided.')
        elif len(auth) > 2:
            raise exceptions.AuthenticationFailed(
                'Invalid token header. Token string should not contain spaces.')

        try:
            token = auth[1].decode()
        except UnicodeError:
            raise exceptions.AuthenticationFailed(
                'Invalid token header. Token string should not contain invalid characters.')

        return self.authenticate_credentials(token)

    def authenticate_credentials(self, key):
        model = self.get_model()
        try:
            token = model.objects.select_related('user').get(key=key)
        except model.DoesNotExist:
            return JsonResponse({
                "error": True, "message": "Invalid Token"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not token.user.is_active:
            return JsonResponse({
                "error": True, "message": "User inactive or deleted"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        return (token.user, token)

    def authenticate_header(self, request):
        return self.keyword


class TokenAuthMiddleware(object):
    """adding profile and company to request object
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        self.process_request(request)
        return self.get_response(request)

    def process_request(self, request):
        try:
            token_auth_user = TokenAuthentication().authenticate(request)
        except exceptions.AuthenticationFailed:
            token_auth_user = None
        if isinstance(token_auth_user, tuple):
            request.user = token_auth_user[0]
        else:
            signin_url = settings.APP_LOGIN_URL
            return HttpResponseRedirect(signin_url)
