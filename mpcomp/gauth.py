#!/usr/bin/env python
#
# Copyright (C) 2009 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


# This module is used for version 2 of the Google Data APIs.


"""Provides auth related token classes and functions for Google Data APIs.

Token classes represent a user's authorization of this app to access their
data. Usually these are not created directly but by a GDClient object.

ClientLoginToken
AuthSubToken
SecureAuthSubToken
OAuthHmacToken
OAuthRsaToken
TwoLeggedOAuthHmacToken
TwoLeggedOAuthRsaToken

Functions which are often used in application code (as opposed to just within
the gdata-python-client library) are the following:

generate_auth_sub_url
authorize_request_token

The following are helper functions which are used to save and load auth token
objects in the App Engine datastore. These should only be used if you are using
this library within App Engine:

ae_load
ae_save
"""


import datetime
import urllib
import urllib.parse
from mpcomp import http_core

try:
    import simplejson
    from simplejson.decoder import JSONDecodeError
except ImportError:
    JSONDecodeError = None
    try:
        # Try to import from django, should work on App Engine
        from django.utils import simplejson
    except ImportError:
        # Should work for Python2.6 and higher.
        import json as simplejson


__author__ = 'j.s@google.com (Jeff Scudder)'


PROGRAMMATIC_AUTH_LABEL = 'GoogleLogin auth='
AUTHSUB_AUTH_LABEL = 'AuthSub token='
OAUTH2_AUTH_LABEL = 'Bearer '


# This dict provides the AuthSub and OAuth scopes for all services by service
# name. The service name (key) is used in ClientLogin requests.
AUTH_SCOPES = {
    'cl': (  # Google Calendar API
        'https://www.google.com/calendar/feeds/',
        'http://www.google.com/calendar/feeds/'),
    'gbase': (  # Google Base API
        'http://base.google.com/base/feeds/',
        'http://www.google.com/base/feeds/'),
    'blogger': (  # Blogger API
        'http://www.blogger.com/feeds/',),
    'codesearch': (  # Google Code Search API
        'http://www.google.com/codesearch/feeds/',),
    'cp': (  # Contacts API
        'https://www.google.com/m8/feeds/',
        'http://www.google.com/m8/feeds/'),
    'finance': (  # Google Finance API
        'http://finance.google.com/finance/feeds/',),
    'health': (  # Google Health API
        'https://www.google.com/health/feeds/',),
    'writely': (  # Documents List API
        'https://docs.google.com/feeds/',
        'https://spreadsheets.google.com/feeds/',
        'https://docs.googleusercontent.com/'),
    'lh2': (  # Picasa Web Albums API
        'http://picasaweb.google.com/data/',),
    'apps': (  # Google Apps Domain Info & Management APIs
        'https://apps-apis.google.com/a/feeds/user/',
        'https://apps-apis.google.com/a/feeds/policies/',
        'https://apps-apis.google.com/a/feeds/alias/',
        'https://apps-apis.google.com/a/feeds/groups/',
        'https://apps-apis.google.com/a/feeds/compliance/audit/',
        'https://apps-apis.google.com/a/feeds/migration/',
        'https://apps-apis.google.com/a/feeds/emailsettings/2.0/'),
    'weaver': (  # Health H9 Sandbox
        'https://www.google.com/h9/feeds/',),
    'wise': (  # Spreadsheets Data API
        'https://spreadsheets.google.com/feeds/',),
    'sitemaps': (  # Google Webmaster Tools API
        'https://www.google.com/webmasters/tools/feeds/',),
    'youtube': (  # YouTube API
        'http://gdata.youtube.com/feeds/api/',
        'http://uploads.gdata.youtube.com/feeds/api',
        'http://gdata.youtube.com/action/GetUploadToken'),
    'books': (  # Google Books API
        'http://www.google.com/books/feeds/',),
    'analytics': (  # Google Analytics API
        'https://www.google.com/analytics/feeds/',),
    'jotspot': (  # Google Sites API
        'http://sites.google.com/feeds/',
        'https://sites.google.com/feeds/'),
    'local': (  # Google Maps Data API
        'http://maps.google.com/maps/feeds/',),
    'code': (  # Project Hosting Data API
        'http://code.google.com/feeds/issues',)}


class Error(Exception):
    pass


class UnsupportedTokenType(Error):

    """Raised when token to or from blob is unable to convert the token."""
    pass


class OAuth2AccessTokenError(Error):

    """Raised when an OAuth2 error occurs."""

    def __init__(self, error_message):
        self.error_message = error_message


class OAuth2RevokeError(Error):

    """Raised when an OAuth2 token revocation was unsuccessful."""

    def __init__(self, http_response, response_body=None):
        """Sets the HTTP information in the error.

        Args:
          http_response: The response from the server, contains error information.
          response_body: string (optional) specified if the response has already
                         been read from the http_response object.
        """
        body = response_body or http_response.read()

        self.status = http_response.status
        self.reason = http_response.reason
        self.body = body
        self.headers = http_core.get_headers(http_response)

        self.error_msg = 'Invalid response %s.' % self.status
        try:
            json_from_body = simplejson.loads(body)
            if isinstance(json_from_body, dict):
                self.error_msg = json_from_body.get('error', self.error_msg)
        except (ValueError, JSONDecodeError):
            pass

    def __str__(self):
        return 'OAuth2RevokeError(status=%i, error=%s)' % (self.status,
                                                           self.error_msg)


REQUEST_TOKEN = 1
AUTHORIZED_REQUEST_TOKEN = 2
ACCESS_TOKEN = 3


class OAuth2Token(object):

    """Token object for OAuth 2.0 as described on
    <http://code.google.com/apis/accounts/docs/OAuth2.html>.

    Token can be applied to a gdata.client.GDClient object using the authorize()
    method, which then signs each request from that object with the OAuth 2.0
    access token.
    This class supports 3 flows of OAuth 2.0:
      Client-side web flow: call generate_authorize_url with `response_type='token''
        and the registered `redirect_uri'.
      Server-side web flow: call generate_authorize_url with the registered
        `redirect_url'.
      Native applications flow: call generate_authorize_url as it is. You will have
        to ask the user to go to the generated url and pass in the authorization
        code to your application.
    """

    def __init__(self, client_id, client_secret, scope, user_agent,
                 auth_uri='https://accounts.google.com/o/oauth2/auth',
                 token_uri='https://accounts.google.com/o/oauth2/token',
                 access_token=None, refresh_token=None,
                 revoke_uri='https://accounts.google.com/o/oauth2/revoke'):
        """Create an instance of OAuth2Token

        Args:
          client_id: string, client identifier.
          client_secret: string client secret.
          scope: string, scope of the credentials being requested.
          user_agent: string, HTTP User-Agent to provide for this application.
          auth_uri: string, URI for authorization endpoint. For convenience
            defaults to Google's endpoints but any OAuth 2.0 provider can be used.
          token_uri: string, URI for token endpoint. For convenience
            defaults to Google's endpoints but any OAuth 2.0 provider can be used.
          revoke_uri: string, URI for revoke endpoint. For convenience
            defaults to Google's endpoints but any OAuth 2.0 provider can be used.
          access_token: string, access token.
          refresh_token: string, refresh token.
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.scope = scope
        self.user_agent = user_agent
        self.auth_uri = auth_uri
        self.token_uri = token_uri
        self.revoke_uri = revoke_uri
        self.access_token = access_token
        self.refresh_token = refresh_token

        # True if the credentials have been revoked or expired and can't be
        # refreshed.
        self._invalid = False

    @property
    def invalid(self):
        """True if the credentials are invalid, such as being revoked."""
        return getattr(self, '_invalid', False)

    def _refresh(self, request):
        """Refresh the access_token using the refresh_token.

        Args:
          request: The atom.http_core.HttpRequest which contains all of the
              information needed to send a request to the remote server.
        """
        body = urllib.parse.urlencode({
            'grant_type': 'refresh_token',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'refresh_token': self.refresh_token
        })
        headers = {
            'user-agent': self.user_agent,
        }

        http_request = http_core.HttpRequest(
            uri=self.token_uri, method='POST', headers=headers)
        http_request.add_body_part(
            body, mime_type='application/x-www-form-urlencoded')
        response = request(http_request)
        body = response.read()
        if response.status == 200:
            self._extract_tokens(body)
        else:
            self._invalid = True
        return response

    def _extract_tokens(self, body):
        d = simplejson.loads(body)
        self.access_token = d['access_token']
        self.refresh_token = d.get('refresh_token', self.refresh_token)
        if 'expires_in' in d:
            self.token_expiry = datetime.timedelta(
                seconds=int(d['expires_in'])) + datetime.datetime.now()
        else:
            self.token_expiry = None

    def authorize(self, client):
        """Authorize a gdata.client.GDClient instance with these credentials.

        Args:
           client: An instance of gdata.client.GDClient
               or something that acts like it.

        Returns:
           A modified instance of client that was passed in.

        Example:
          >>> c = gdata.client.GDClient(source='user-agent')
          >>> c = token.authorize(c)
        """
        client.auth_token = self
        request_orig = client.http_client.request

        def new_request(http_request):
            response = request_orig(http_request)
            if response.status == 401:
                refresh_response = self._refresh(request_orig)
                if self._invalid:
                    return refresh_response
                self.modify_request(http_request)
                return request_orig(http_request)
            return response

        client.http_client.request = new_request
        return client

    def modify_request(self, http_request):
        """Sets the Authorization header in the HTTP request using the token.

        Returns:
          The same HTTP request object which was passed in.
        """
        http_request.headers['Authorization'] = '%s%s' % (OAUTH2_AUTH_LABEL,
                                                          self.access_token)
        return http_request

    ModifyRequest = modify_request


def _make_credentials_property(name):
    """Helper method which generates properties.

    Used to access and set values on credentials property as if they were native
    attributes on the current object.

    Args:
      name: A string corresponding to the attribute being accessed on the
          credentials attribute of the object which will own the property.

    Returns:
      An instance of `property` which is a proxy for the `name` attribute on the
          credentials attribute of the object.
    """

    def get_credentials_value(self):
        return getattr(self.credentials, name)

    def set_credentials_value(self, value):
        setattr(self.credentials, name, value)
    return property(get_credentials_value, set_credentials_value)
