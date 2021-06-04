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
from mpcomp import client
from mpcomp import data
from mpcomp import gauth

"""Contains a client to communicate with the Contacts servers.

For documentation on the Contacts API, see:
http://code.google.com/apis/contatcs/
"""

__author__ = "vinces1979@gmail.com (Vince Spicer)"


DEFAULT_BATCH_URL = "https://www.google.com/m8/feeds/contacts/default/full" "/batch"
DEFAULT_PROFILES_BATCH_URL = (
    "https://www.google.com/m8/feeds/profiles/domain/" "%s/full/batch"
)


class ContactsClient(client.GDClient):
    api_version = "3"
    auth_service = "cp"
    server = "www.google.com"
    contact_list = "default"
    auth_scopes = gauth.AUTH_SCOPES["cp"]
    ssl = True

    def __init__(self, domain=None, auth_token=None, **kwargs):
        """Constructs a new client for the Email Settings API.

        Args:
          domain: string The Google Apps domain (if any).
          kwargs: The other parameters to pass to the client.GDClient
              constructor.
        """
        client.GDClient.__init__(self, auth_token=auth_token, **kwargs)
        self.domain = domain

    def get_feed_uri(
        self, kind="contacts", contact_list=None, projection="full", scheme="https"
    ):
        """Builds a feed URI.

        Args:
          kind: The type of feed to return, typically 'groups' or 'contacts'.
            Default value: 'contacts'.
          contact_list: The contact list to return a feed for.
            Default value: self.contact_list.
          projection: The projection to apply to the feed contents, for example
            'full', 'base', 'base/12345', 'full/batch'. Default value: 'full'.
          scheme: The URL scheme such as 'http' or 'https', None to return a
              relative URI without hostname.

        Returns:
          A feed URI using the given kind, contact list, and projection.
          Example: '/m8/feeds/contacts/default/full'.
        """
        contact_list = contact_list or self.contact_list
        if kind == "profiles":
            contact_list = "domain/%s" % self.domain
        prefix = scheme and "%s://%s" % (scheme, self.server) or ""
        return "%s/m8/feeds/%s/%s/%s" % (prefix, kind, contact_list, projection)

    GetFeedUri = get_feed_uri

    def get_contact(
        self, uri, desired_class=data.ContactEntry, auth_token=None, **kwargs
    ):
        return self.get_entry(
            uri, auth_token=auth_token, desired_class=desired_class, **kwargs
        )

    GetContact = get_contact

    def get_contacts(
        self, uri=None, desired_class=data.ContactsFeed, auth_token=None, **kwargs
    ):
        """Obtains a feed with the contacts belonging to the current user.

        Args:
          auth_token: An object which sets the Authorization HTTP header in its
                      modify_request method. Recommended classes include
                      gauth.ClientLoginToken and gauth.AuthSubToken
                      among others. Represents the current user. Defaults to None
                      and if None, this method will look for a value in the
                      auth_token member of SpreadsheetsClient.
          desired_class: class descended from atom.core.XmlElement to which a
                         successful response should be converted. If there is no
                         converter function specified (desired_class=None) then the
                         desired_class will be used in calling the
                         atom.core.parse function. If neither
                         the desired_class nor the converter is specified, an
                         HTTP reponse object will be returned. Defaults to
                         spreadsheets.data.SpreadsheetsFeed.
        """
        uri = uri or self.GetFeedUri()
        print(
            self.get_feed(
                uri, auth_token=auth_token, desired_class=desired_class, **kwargs
            )
        )
        return self.get_feed(
            uri, auth_token=auth_token, desired_class=desired_class, **kwargs
        )

    GetContacts = get_contacts

    def get_group(
        self, uri=None, desired_class=data.GroupEntry, auth_token=None, **kwargs
    ):
        """Get a single groups details
        Args:
            uri:  the group uri or id
        """
        return self.get_entry(
            uri, desired_class=desired_class, auth_token=auth_token, **kwargs
        )

    GetGroup = get_group

    def get_groups(
        self, uri=None, desired_class=data.GroupsFeed, auth_token=None, **kwargs
    ):
        uri = uri or self.GetFeedUri("groups")
        return self.get_feed(
            uri, desired_class=desired_class, auth_token=auth_token, **kwargs
        )

    GetGroups = get_groups

    def get_photo(self, contact_entry_or_url, auth_token=None, **kwargs):
        """Retrives the binary data for the contact's profile photo as a string.

        Args:
          contact_entry_or_url: a ContactEntry object or a string
             containing the photo link's URL. If the contact entry does not
             contain a photo link, the image will not be fetched and this method
             will return None.
        """
        # TODO: add the ability to write out the binary image data to a file,
        # reading and writing a chunk at a time to avoid potentially using up
        # large amounts of memory.
        url = None
        if isinstance(contact_entry_or_url, data.ContactEntry):
            photo_link = contact_entry_or_url.GetPhotoLink()
            if photo_link:
                url = photo_link.href
        else:
            url = contact_entry_or_url
        if url:
            return self.Get(url, auth_token=auth_token, **kwargs).read()
        return None

    GetPhoto = get_photo

    def get_profiles_feed(self, uri=None, auth_token=None, **kwargs):
        """Retrieves a feed containing all domain's profiles.

        Args:
          uri: string (optional) the URL to retrieve the profiles feed,
              for example /m8/feeds/profiles/default/full

        Returns:
          On success, a ProfilesFeed containing the profiles.
          On failure, raises a RequestError.
        """

        uri = uri or self.GetFeedUri("profiles")
        return self.get_feed(
            uri, auth_token=auth_token, desired_class=data.ProfilesFeed, **kwargs
        )

    GetProfilesFeed = get_profiles_feed

    def get_profile(self, uri, auth_token=None, **kwargs):
        """Retrieves a domain's profile for the user.

        Args:
          uri: string the URL to retrieve the profiles feed,
              for example /m8/feeds/profiles/default/full/username

        Returns:
          On success, a ProfileEntry containing the profile for the user.
          On failure, raises a RequestError
        """
        return self.get_entry(
            uri, desired_class=data.ProfileEntry, auth_token=auth_token, **kwargs
        )

    GetProfile = get_profile

    def update_profile(self, updated_profile, auth_token=None, force=False, **kwargs):
        """Updates an existing profile.

        Args:
          updated_profile: atom.Entry or subclass containing
                           the Atom Entry which will replace the profile which is
                           stored at the edit_url.
          auth_token: An object which sets the Authorization HTTP header in its
                      modify_request method. Recommended classes include
                      gauth.ClientLoginToken and gauth.AuthSubToken
                      among others. Represents the current user. Defaults to None
                      and if None, this method will look for a value in the
                      auth_token member of ContactsClient.
          force: boolean stating whether an update should be forced. Defaults to
                 False. Normally, if a change has been made since the passed in
                 entry was obtained, the server will not overwrite the entry since
                 the changes were based on an obsolete version of the entry.
                 Setting force to True will cause the update to silently
                 overwrite whatever version is present.
          url_params: dict (optional) Additional URL parameters to be included
                      in the insertion request.
          escape_params: boolean (optional) If true, the url_parameters will be
                         escaped before they are included in the request.

        Returns:
          On successful update,  a httplib.HTTPResponse containing the server's
            response to the PUT request.
          On failure, raises a RequestError.
        """
        return self.Update(
            updated_profile, auth_token=auth_token, force=force, **kwargs
        )

    UpdateProfile = update_profile

    def execute_batch(
        self,
        batch_feed,
        url=DEFAULT_BATCH_URL,
        desired_class=None,
        auth_token=None,
        **kwargs
    ):
        """Sends a batch request feed to the server.

        Args:
          batch_feed: ContactFeed A feed containing batch
              request entries. Each entry contains the operation to be performed
              on the data contained in the entry. For example an entry with an
              operation type of insert will be used as if the individual entry
              had been inserted.
          url: str The batch URL to which these operations should be applied.
          converter: Function (optional) The function used to convert the server's
              response to an object.

        Returns:
          The results of the batch request's execution on the server. If the
          default converter is used, this is stored in a ContactsFeed.
        """
        return self.Post(
            batch_feed, url, desired_class=desired_class, auth_token=None, **kwargs
        )

    ExecuteBatch = execute_batch

    def execute_batch_profiles(
        self,
        batch_feed,
        url=None,
        desired_class=data.ProfilesFeed,
        auth_token=None,
        **kwargs
    ):
        """Sends a batch request feed to the server.

        Args:
          batch_feed: profiles.ProfilesFeed A feed containing batch
              request entries. Each entry contains the operation to be performed
              on the data contained in the entry. For example an entry with an
              operation type of insert will be used as if the individual entry
              had been inserted.
          url: string The batch URL to which these operations should be applied.
          converter: Function (optional) The function used to convert the server's
              response to an object. The default value is
              profiles.ProfilesFeedFromString.

        Returns:
          The results of the batch request's execution on the server. If the
          default converter is used, this is stored in a ProfilesFeed.
        """
        url = url or (DEFAULT_PROFILES_BATCH_URL % self.domain)
        return self.Post(
            batch_feed,
            url,
            desired_class=desired_class,
            auth_token=auth_token,
            **kwargs
        )

    ExecuteBatchProfiles = execute_batch_profiles

    def _CleanUri(self, uri):
        """Sanitizes a feed URI.

        Args:
          uri: The URI to sanitize, can be relative or absolute.

        Returns:
          The given URI without its http://server prefix, if any.
          Keeps the leading slash of the URI.
        """
        url_prefix = "http://%s" % self.server
        if uri.startswith(url_prefix):
            uri = uri[len(url_prefix) :]
        return uri


class ContactsQuery(client.Query):

    """
    Create a custom Contacts Query

    Full specs can be found at: U{Contacts query parameters reference
    <http://code.google.com/apis/contacts/docs/3.0/reference.html#Parameters>}
    """

    def __init__(
        self,
        feed=None,
        group=None,
        orderby=None,
        showdeleted=None,
        sortorder=None,
        requirealldeleted=None,
        **kwargs
    ):
        """
        @param max_results: The maximum number of entries to return. If you want
            to receive all of the contacts, rather than only the default maximum, you
            can specify a very large number for max-results.
        @param start-index: The 1-based index of the first result to be retrieved.
        @param updated-min: The lower bound on entry update dates.
        @param group: Constrains the results to only the contacts belonging to the
            group specified. Value of this parameter specifies group ID
        @param orderby:  Sorting criterion. The only supported value is
            lastmodified.
        @param showdeleted: Include deleted contacts in the returned contacts feed
        @pram sortorder: Sorting order direction. Can be either ascending or
            descending.
        @param requirealldeleted: Only relevant if showdeleted and updated-min
            are also provided. It dictates the behavior of the server in case it
            detects that placeholders of some entries deleted since the point in
            time specified as updated-min may have been lost.
        """
        client.Query.__init__(self, **kwargs)
        self.group = group
        self.orderby = orderby
        self.sortorder = sortorder
        self.showdeleted = showdeleted

    def modify_request(self, http_request):
        if self.group:
            client._add_query_param("group", self.group, http_request)
        if self.orderby:
            client._add_query_param("orderby", self.orderby, http_request)
        if self.sortorder:
            client._add_query_param("sortorder", self.sortorder, http_request)
        if self.showdeleted:
            client._add_query_param("showdeleted", self.showdeleted, http_request)
        client.Query.modify_request(self, http_request)

    ModifyRequest = modify_request
