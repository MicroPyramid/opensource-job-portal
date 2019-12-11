#!/usr/bin/env python
#
# Copyright (C) 2008, 2009 Google Inc.
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


"""Provides a client to interact with Google Data API servers.

This module is used for version 2 of the Google Data APIs. The primary class
in this module is GDClient.

  GDClient: handles auth and CRUD operations when communicating with servers.
  GDataClient: deprecated client for version one services. Will be removed.
"""


__author__ = 'j.s@google.com (Jeff Scudder)'


from mpcomp import atom_client
from mpcomp import core
from mpcomp import http_core
from mpcomp import gdata_data


class Error(Exception):
    pass


class RequestError(Error):
    status = None
    reason = None
    body = None
    headers = None


class RedirectError(RequestError):
    pass


class CaptchaChallenge(RequestError):
    captcha_url = None
    captcha_token = None


class ClientLoginTokenMissing(Error):
    pass


class MissingOAuthParameters(Error):
    pass


class ClientLoginFailed(RequestError):
    pass


class UnableToUpgradeToken(RequestError):
    pass


class Unauthorized(Error):
    pass


class BadAuthenticationServiceURL(RedirectError):
    pass


class BadAuthentication(RequestError):
    pass


class NotModified(RequestError):
    pass


class NotImplemented(RequestError):
    pass


def error_from_response(message, http_response, error_class,
                        response_body=None):
    """Creates a new exception and sets the HTTP information in the error.

    Args:
     message: str human readable message to be displayed if the exception is
              not caught.
     http_response: The response from the server, contains error information.
     error_class: The exception to be instantiated and populated with
                  information from the http_response
     response_body: str (optional) specify if the response has already been read
                    from the http_response object.
    """
    if response_body is None:
        body = http_response.read()
    else:
        body = response_body
    error = error_class('%s: %i, %s' % (message, http_response.status, body))
    error.status = http_response.status
    error.reason = http_response.reason
    error.body = body
    error.headers = http_core.get_headers(http_response)
    return error


def get_xml_version(version):
    """Determines which XML schema to use based on the client API version.

    Args:
      version: string which is converted to an int. The version string is in
               the form 'Major.Minor.x.y.z' and only the major version number
               is considered. If None is provided assume version 1.
    """
    if version is None:
        return 1
    return int(version.split('.')[0])


class GDClient(atom_client.AtomPubClient):

    """Communicates with Google Data servers to perform CRUD operations.

    This class is currently experimental and may change in backwards
    incompatible ways.

    This class exists to simplify the following three areas involved in using
    the Google Data APIs.

    CRUD Operations:

    The client provides a generic 'request' method for making HTTP requests.
    There are a number of convenience methods which are built on top of
    request, which include get_feed, get_entry, get_next, post, update, and
    delete. These methods contact the Google Data servers.

    Auth:

    Reading user-specific private data requires authorization from the user as
    do any changes to user data. An auth_token object can be passed into any
    of the HTTP requests to set the Authorization header in the request.

    You may also want to set the auth_token member to a an object which can
    use modify_request to set the Authorization header in the HTTP request.

    If you are authenticating using the email address and password, you can
    use the client_login method to obtain an auth token and set the
    auth_token member.

    If you are using browser redirects, specifically AuthSub, you will want
    to use gdata.gauth.AuthSubToken.from_url to obtain the token after the
    redirect, and you will probably want to updgrade this since use token
    to a multiple use (session) token using the upgrade_token method.

    API Versions:

    This client is multi-version capable and can be used with Google Data API
    version 1 and version 2. The version should be specified by setting the
    api_version member to a string, either '1' or '2'.
    """

    # The gsessionid is used by Google Calendar to prevent redirects.
    __gsessionid = None
    api_version = None
    # Name of the Google Data service when making a ClientLogin request.
    auth_service = None
    # URL prefixes which should be requested for AuthSub and OAuth.
    auth_scopes = None
    # Name of alternate auth service to use in certain cases
    alt_auth_service = None

    def request(self, method=None, uri=None, auth_token=None,
                http_request=None, converter=None, desired_class=None,
                redirects_remaining=4, **kwargs):
        """Make an HTTP request to the server.

        See also documentation for atom_client.AtomPubClient.request.

        If a 302 redirect is sent from the server to the client, this client
        assumes that the redirect is in the form used by the Google Calendar API.
        The same request URI and method will be used as in the original request,
        but a gsessionid URL parameter will be added to the request URI with
        the value provided in the server's 302 redirect response. If the 302
        redirect is not in the format specified by the Google Calendar API, a
        RedirectError will be raised containing the body of the server's
        response.

        The method calls the client's modify_request method to make any changes
        required by the client before the request is made. For example, a
        version 2 client could add a GData-Version: 2 header to the request in
        its modify_request method.

        Args:
          method: str The HTTP verb for this request, usually 'GET', 'POST',
                  'PUT', or 'DELETE'
          uri: http_core.Uri, str, or unicode The URL being requested.
          auth_token: An object which sets the Authorization HTTP header in its
                      modify_request method. Recommended classes include
                      gdata.gauth.ClientLoginToken and gdata.gauth.AuthSubToken
                      among others.
          http_request: (optional) http_core.HttpRequest
          converter: function which takes the body of the response as its only
                     argument and returns the desired object.
          desired_class: class descended from core.XmlElement to which a
                         successful response should be converted. If there is no
                         converter function specified (converter=None) then the
                         desired_class will be used in calling the
                         core.parse function. If neither
                         the desired_class nor the converter is specified, an
                         HTTP reponse object will be returned.
          redirects_remaining: (optional) int, if this number is 0 and the
                               server sends a 302 redirect, the request method
                               will raise an exception. This parameter is used in
                               recursive request calls to avoid an infinite loop.

        Any additional arguments are passed through to
        atom_client.AtomPubClient.request.

        Returns:
          An HTTP response object (see http_core.HttpResponse for a
          description of the object's interface) if no converter was
          specified and no desired_class was specified. If a converter function
          was provided, the results of calling the converter are returned. If no
          converter was specified but a desired_class was provided, the response
          body will be converted to the class using
          core.parse.
        """
        if isinstance(uri, str):
            uri = http_core.Uri.parse_uri(uri)

        # Add the gsession ID to the URL to prevent further redirects.
        # TODO: If different sessions are using the same client, there will be a
        # multitude of redirects and session ID shuffling.
        # If the gsession ID is in the URL, adopt it as the standard location.
        if uri is not None and uri.query is not None and 'gsessionid' in uri.query:
            self.__gsessionid = uri.query['gsessionid']
        # The gsession ID could also be in the HTTP request.
        elif (http_request is not None and http_request.uri is not None
              and http_request.uri.query is not None
              and 'gsessionid' in http_request.uri.query):
            self.__gsessionid = http_request.uri.query['gsessionid']
        # If the gsession ID is stored in the client, and was not present in the
        # URI then add it to the URI.
        elif self.__gsessionid is not None:
            uri.query['gsessionid'] = self.__gsessionid

        # The AtomPubClient should call this class' modify_request before
        # performing the HTTP request.
        #http_request = self.modify_request(http_request)

        response = atom_client.AtomPubClient.request(self, method=method,
                                                     uri=uri, auth_token=auth_token, http_request=http_request, **kwargs)
        # On success, convert the response body using the desired converter
        # function if present.
        # print (response)
        print(response.status)
        if response is None:
            return None
        if response.status == 200 or response.status == 201:
            # print (converter)
            # print (desired_class)
            if converter is not None:
                return converter(response)
            elif desired_class is not None:
                # print (self.api_version)
                if self.api_version is not None:
                    return core.parse(response.read(), desired_class,
                                      version=get_xml_version(self.api_version))
                # No API version was specified, so allow parse to
                # use the default version.
                return core.parse(response.read(), desired_class)
            return response
        # TODO: move the redirect logic into the Google Calendar client once it
        # exists since the redirects are only used in the calendar API.
        elif response.status == 302:
            if redirects_remaining > 0:
                location = (response.getheader('Location')
                            or response.getheader('location'))
                if location is not None:
                    # Make a recursive call with the gsession ID in the URI to follow
                    # the redirect.
                    return self.request(method=method, uri=location,
                                        auth_token=auth_token, http_request=http_request,
                                        converter=converter, desired_class=desired_class,
                                        redirects_remaining=redirects_remaining -
                                        1,
                                        **kwargs)
                else:
                    raise error_from_response('302 received without Location header',
                                              response, RedirectError)
            else:
                raise error_from_response('Too many redirects from server',
                                          response, RedirectError)
        elif response.status == 401:
            raise error_from_response('Unauthorized - Server responded with',
                                      response, Unauthorized)
        elif response.status == 304:
            raise error_from_response('Entry Not Modified - Server responded with',
                                      response, NotModified)
        elif response.status == 501:
            raise error_from_response(
                'This API operation is not implemented. - Server responded with',
                response, NotImplemented)
        # If the server's response was not a 200, 201, 302, 304, 401, or 501, raise
        # an exception.
        else:
            raise error_from_response('Server responded with', response,
                                      RequestError)

    def modify_request(self, http_request):
        """Adds or changes request before making the HTTP request.

        This client will add the API version if it is specified.
        Subclasses may override this method to add their own request
        modifications before the request is made.
        """
        http_request = atom_client.AtomPubClient.modify_request(self,
                                                                http_request)
        if self.api_version is not None:
            http_request.headers['GData-Version'] = self.api_version
        return http_request

    ModifyRequest = modify_request

    def get_feed(self, uri, auth_token=None, converter=None,
                 desired_class=gdata_data.GDFeed, **kwargs):
        abc = self.request(method='GET', uri=uri, auth_token=auth_token,
                           converter=converter, desired_class=desired_class,
                           **kwargs)
        print(abc)
        return self.request(method='GET', uri=uri, auth_token=auth_token,
                            converter=converter, desired_class=desired_class,
                            **kwargs)

    GetFeed = get_feed

    def get_entry(self, uri, auth_token=None, converter=None,
                  desired_class=gdata_data.GDEntry, etag=None, **kwargs):
        http_request = http_core.HttpRequest()
        # Conditional retrieval
        if etag is not None:
            http_request.headers['If-None-Match'] = etag
        return self.request(method='GET', uri=uri, auth_token=auth_token,
                            http_request=http_request, converter=converter,
                            desired_class=desired_class, **kwargs)

    GetEntry = get_entry

    def get_next(self, feed, auth_token=None, converter=None,
                 desired_class=None, **kwargs):
        """Fetches the next set of results from the feed.

        When requesting a feed, the number of entries returned is capped at a
        service specific default limit (often 25 entries). You can specify your
        own entry-count cap using the max-results URL query parameter. If there
        are more results than could fit under max-results, the feed will contain
        a next link. This method performs a GET against this next results URL.

        Returns:
          A new feed object containing the next set of entries in this feed.
        """
        if converter is None and desired_class is None:
            desired_class = feed.__class__
        return self.get_feed(feed.find_next_link(), auth_token=auth_token,
                             converter=converter, desired_class=desired_class,
                             **kwargs)

    GetNext = get_next

    # TODO: add a refresh method to re-fetch the entry/feed from the server
    # if it has been updated.

    def post(self, entry, uri, auth_token=None, converter=None,
             desired_class=None, **kwargs):
        if converter is None and desired_class is None:
            desired_class = entry.__class__
        http_request = http_core.HttpRequest()
        http_request.add_body_part(
            entry.to_string(get_xml_version(self.api_version)),
            'application/atom+xml')
        return self.request(method='POST', uri=uri, auth_token=auth_token,
                            http_request=http_request, converter=converter,
                            desired_class=desired_class, **kwargs)

    Post = post

    def update(self, entry, auth_token=None, force=False, uri=None, **kwargs):
        """Edits the entry on the server by sending the XML for this entry.

        Performs a PUT and converts the response to a new entry object with a
        matching class to the entry passed in.

        Args:
          entry:
          auth_token:
          force: boolean stating whether an update should be forced. Defaults to
                 False. Normally, if a change has been made since the passed in
                 entry was obtained, the server will not overwrite the entry since
                 the changes were based on an obsolete version of the entry.
                 Setting force to True will cause the update to silently
                 overwrite whatever version is present.
          uri: The uri to put to. If provided, this uri is PUT to rather than the
               inferred uri from the entry's edit link.

        Returns:
          A new Entry object of a matching type to the entry which was passed in.
        """
        http_request = http_core.HttpRequest()
        http_request.add_body_part(
            entry.to_string(get_xml_version(self.api_version)),
            'application/atom+xml')
        # Include the ETag in the request if present.
        if force:
            http_request.headers['If-Match'] = '*'
        elif hasattr(entry, 'etag') and entry.etag:
            http_request.headers['If-Match'] = entry.etag

        if uri is None:
            uri = entry.find_edit_link()

        return self.request(method='PUT', uri=uri, auth_token=auth_token,
                            http_request=http_request,
                            desired_class=entry.__class__, **kwargs)

    Update = update

    def delete(self, entry_or_uri, auth_token=None, force=False, **kwargs):
        http_request = http_core.HttpRequest()

        # Include the ETag in the request if present.
        if force:
            http_request.headers['If-Match'] = '*'
        elif hasattr(entry_or_uri, 'etag') and entry_or_uri.etag:
            http_request.headers['If-Match'] = entry_or_uri.etag

        # If the user passes in a URL, just delete directly, may not work as
        # the service might require an ETag.
        if isinstance(entry_or_uri, (str, http_core.Uri)):
            return self.request(method='DELETE', uri=entry_or_uri,
                                http_request=http_request, auth_token=auth_token,
                                **kwargs)

        return self.request(method='DELETE', uri=entry_or_uri.find_edit_link(),
                            http_request=http_request, auth_token=auth_token,
                            **kwargs)

    Delete = delete

    def batch(self, feed, uri=None, force=False, auth_token=None, **kwargs):
        """Sends a batch request to the server to execute operation entries.

        Args:
          feed: A batch feed containing batch entries, each is an operation.
          uri: (optional) The uri to which the batch request feed should be POSTed.
              If none is provided, then the feed's edit link will be used.
          force: (optional) boolean set to True if you want the batch update to
              clobber all data. If False, the version in the information in the
              feed object will cause the server to check to see that no changes
              intervened between when you fetched the data and when you sent the
              changes.
          auth_token: (optional) An object which sets the Authorization HTTP header
              in its modify_request method. Recommended classes include
              gdata.gauth.ClientLoginToken and gdata.gauth.AuthSubToken
              among others.
        """
        http_request = http_core.HttpRequest()
        http_request.add_body_part(
            feed.to_string(get_xml_version(self.api_version)),
            'application/atom+xml')
        if force:
            http_request.headers['If-Match'] = '*'
        elif hasattr(feed, 'etag') and feed.etag:
            http_request.headers['If-Match'] = feed.etag

        if uri is None:
            uri = feed.find_edit_link()

        return self.request(method='POST', uri=uri, auth_token=auth_token,
                            http_request=http_request,
                            desired_class=feed.__class__, **kwargs)

    Batch = batch

    # TODO: add a refresh method to request a conditional update to an entry
    # or feed.


def _add_query_param(param_string, value, http_request):
    if value:
        http_request.uri.query[param_string] = value


class Query(object):

    def __init__(self, text_query=None, categories=None, author=None, alt=None,
                 updated_min=None, updated_max=None, pretty_print=False,
                 published_min=None, published_max=None, start_index=None,
                 max_results=None, strict=False, **custom_parameters):
        """Constructs a Google Data Query to filter feed contents serverside.

        Args:
          text_query: Full text search str (optional)
          categories: list of strings (optional). Each string is a required
              category. To include an 'or' query, put a | in the string between
              terms. For example, to find everything in the Fitz category and
              the Laurie or Jane category (Fitz and (Laurie or Jane)) you would
              set categories to ['Fitz', 'Laurie|Jane'].
          author: str (optional) The service returns entries where the author
              name and/or email address match your query string.
          alt: str (optional) for the Alternative representation type you'd like
              the feed in. If you don't specify an alt parameter, the service
              returns an Atom feed. This is equivalent to alt='atom'.
              alt='rss' returns an RSS 2.0 result feed.
              alt='json' returns a JSON representation of the feed.
              alt='json-in-script' Requests a response that wraps JSON in a script
              tag.
              alt='atom-in-script' Requests an Atom response that wraps an XML
              string in a script tag.
              alt='rss-in-script' Requests an RSS response that wraps an XML
              string in a script tag.
          updated_min: str (optional), RFC 3339 timestamp format, lower bounds.
              For example: 2005-08-09T10:57:00-08:00
          updated_max: str (optional) updated time must be earlier than timestamp.
          pretty_print: boolean (optional) If True the server's XML response will
              be indented to make it more human readable. Defaults to False.
          published_min: str (optional), Similar to updated_min but for published
              time.
          published_max: str (optional), Similar to updated_max but for published
              time.
          start_index: int or str (optional) 1-based index of the first result to
              be retrieved. Note that this isn't a general cursoring mechanism.
              If you first send a query with ?start-index=1&max-results=10 and
              then send another query with ?start-index=11&max-results=10, the
              service cannot guarantee that the results are equivalent to
              ?start-index=1&max-results=20, because insertions and deletions
              could have taken place in between the two queries.
          max_results: int or str (optional) Maximum number of results to be
              retrieved. Each service has a default max (usually 25) which can
              vary from service to service. There is also a service-specific
              limit to the max_results you can fetch in a request.
          strict: boolean (optional) If True, the server will return an error if
              the server does not recognize any of the parameters in the request
              URL. Defaults to False.
          custom_parameters: other query parameters that are not explicitly defined.
        """
        self.text_query = text_query
        self.categories = categories or []
        self.author = author
        self.alt = alt
        self.updated_min = updated_min
        self.updated_max = updated_max
        self.pretty_print = pretty_print
        self.published_min = published_min
        self.published_max = published_max
        self.start_index = start_index
        self.max_results = max_results
        self.strict = strict
        self.custom_parameters = custom_parameters

    def add_custom_parameter(self, key, value):
        self.custom_parameters[key] = value

    AddCustomParameter = add_custom_parameter

    def modify_request(self, http_request):
        _add_query_param('q', self.text_query, http_request)
        if self.categories:
            http_request.uri.query['category'] = ','.join(self.categories)
        _add_query_param('author', self.author, http_request)
        _add_query_param('alt', self.alt, http_request)
        _add_query_param('updated-min', self.updated_min, http_request)
        _add_query_param('updated-max', self.updated_max, http_request)
        if self.pretty_print:
            http_request.uri.query['prettyprint'] = 'true'
        _add_query_param('published-min', self.published_min, http_request)
        _add_query_param('published-max', self.published_max, http_request)
        if self.start_index is not None:
            http_request.uri.query['start-index'] = str(self.start_index)
        if self.max_results is not None:
            http_request.uri.query['max-results'] = str(self.max_results)
        if self.strict:
            http_request.uri.query['strict'] = 'true'
        http_request.uri.query.update(self.custom_parameters)

    ModifyRequest = modify_request


class GDQuery(http_core.Uri):

    def _get_text_query(self):
        return self.query['q']

    def _set_text_query(self, value):
        self.query['q'] = value

    text_query = property(_get_text_query, _set_text_query,
                          doc='The q parameter for searching for an exact text match on content')
