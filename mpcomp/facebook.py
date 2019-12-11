

import urllib
try:
    import urllib.request as urllib2
except ImportError:
    import urllib2
    import hashlib
import hmac
import base64
import socket
import requests

# Find a JSON parser
try:
    import simplejson as json
except ImportError:
    try:
        from django.utils import simplejson as json
    except ImportError:
        import json
_parse_json = json.loads

# Find a query string parser
# try:
#     from urlparse import parse_qs
# except ImportError:
#     from cgi import parse_qs


class GraphAPI(object):
    def __init__(self, access_token=None, timeout=None):
        self.access_token = access_token
        self.timeout = timeout

    def get_object(self, id, **args):
        return self.request(id, args)

    def get_objects(self, ids, **args):
        args["ids"] = ",".join(ids)
        return self.request("", args)

    def get_connections(self, id, connection_name, **args):
        return self.request(id + "/" + connection_name, args)

    def put_object(self, parent_object, connection_name, **data):
        if self.access_token:
            return self.request(parent_object + "/" + connection_name,post_args=data)
        else:
            raise AssertionError("access token not provided")

    def delete_object(self, id):
        """Deletes the object with the given ID from the graph."""
        # x=self.request(id, post_args={"method": "delete"})
        params = urllib.parse.urlencode({"method": "delete", 'access_token': str(id)})
        u = requests.get("https://graph.facebook.com/" + str(id) + "?" + params)
        groups = u.json()
        return groups

    def request(self, path, args=None, post_args=None):

        args = args or {}

        if self.access_token:
            if post_args is not None:
                post_args["access_token"] = self.access_token
            else:
                args["access_token"] = self.access_token
        post_data = None if post_args is None else urllib.urlencode(post_args)
        try:
            file = urllib2.urlopen("https://graph.facebook.com/" + path + "?" +
                                   urllib.parse.urlencode(args),
                                   post_data, timeout=self.timeout)
        except (urllib2.HTTPError, error):
            response = _parse_json(error.read())
            raise GraphAPIError(response)
        except TypeError:
            # Timeout support for Python <2.6
            if self.timeout:
                socket.setdefaulttimeout(self.timeout)
            file = urllib2.urlopen("https://graph.facebook.com/" + path + "?" +
                                   urllib.parse.urlencode(args), post_data)
        try:
            # fileInfo = file.info()
            response = ''
            response = _parse_json(file.read())
        finally:
            file.close()
        if response and isinstance(response, dict) and response.get("error"):
            raise GraphAPIError(response["error"]["type"],
                                response["error"]["message"])
        return response

    def fql(self, query, args=None, post_args=None):
        """FQL query.

        Example query: "SELECT affiliations FROM user WHERE uid = me()"

        """
        args = args or {}
        if self.access_token:
            if post_args is not None:
                post_args["access_token"] = self.access_token
            else:
                args["access_token"] = self.access_token
        post_data = None if post_args is None else urllib.urlencode(post_args)

        """Check if query is a dict and
           use the multiquery method
           else use single query
        """
        if not isinstance(query, basestring):
            args["queries"] = query
            fql_method = 'fql.multiquery'
        else:
            args["query"] = query
            fql_method = 'fql.query'

        args["format"] = "json"

        try:
            file = urllib2.urlopen("https://api.facebook.com/method/" +
                                   fql_method + "?" + urllib.urlencode(args),
                                   post_data, timeout=self.timeout)
        except TypeError:
            # Timeout support for Python <2.6
            if self.timeout:
                socket.setdefaulttimeout(self.timeout)
            file = urllib2.urlopen("https://api.facebook.com/method/" +
                                   fql_method + "?" + urllib.urlencode(args),
                                   post_data)

        try:
            content = file.read()
            response = _parse_json(content)
            #Return a list if success, return a dictionary if failed
            if type(response) is dict and "error_code" in response:
                raise GraphAPIError(response)
        except:
            pass
        finally:
            file.close()

        return response
    def extend_access_token(self, app_id, app_secret):
        """
        Extends the expiration time of a valid OAuth access token. See
        <https://developers.facebook.com/roadmap/offline-access-removal/
        #extend_token>

        """
        args = {
            "client_id": app_id,
            "client_secret": app_secret,
            "grant_type": "fb_exchange_token",
            "fb_exchange_token": self.access_token,
        }
        response = urllib2.urlopen("https://graph.facebook.com/oauth/"
                                   "access_token?" +
                                   urllib.parse.urlencode(args)).read().decode('utf-8')
        query_str = json.loads(str(response))
        if "access_token" in query_str:
            result = {"accesstoken": query_str["access_token"]}
            if "expires" in query_str:
                result["expire"] = query_str["expires"]
            return result
        else:
            response = json.loads(response)
            raise GraphAPIError(response)


class GraphAPIError(Exception):
    def __init__(self, result):
        #Exception.__init__(self, message)
        #self.type = type
        self.result = result
        try:
            self.type = result["error_code"]
        except:
            self.type = ""

        # OAuth 2.0 Draft 10
        try:
            self.message = result["error_description"]
        except:
            # OAuth 2.0 Draft 00
            try:
                self.message = result["error"]["message"]
            except:
                # REST server style
                try:
                    self.message = result["error_msg"]
                except:
                    self.message = result

        Exception.__init__(self, self.message)


def get_user_from_cookie(cookies, app_id, app_secret):
    
    cookie = cookies.get("fbsr_" + app_id, "")
    if not cookie:
        return None
    parsed_request = parse_signed_request(cookie, app_secret)
    if not parsed_request:
        return None
    try:
        result = get_access_token_from_code(parsed_request["code"], "",app_id, app_secret)
    except GraphAPIError:
        return None
    result["uid"] = parsed_request["user_id"]
    return result


def parse_signed_request(signed_request, app_secret):

    try:
        l = signed_request.split('.', 2)
        encoded_sig = str(l[0])
        payload = str(l[1])
        sig = base64.urlsafe_b64decode(encoded_sig + "=" *
                                       ((4 - len(encoded_sig) % 4) % 4))
        data = base64.urlsafe_b64decode(payload + "=" *
                                        ((4 - len(payload) % 4) % 4))
    except IndexError:
        # Signed request was malformed.
        return False
    except TypeError:
        # Signed request had a corrupted payload.
        return False

    data = _parse_json(data)
    if data.get('algorithm', '').upper() != 'HMAC-SHA256':
        return False

    # HMAC can only handle ascii (byte) strings
    # http://bugs.python.org/issue5285
    app_secret = app_secret.encode('ascii')
    payload = payload.encode('ascii')

    expected_sig = hmac.new(app_secret,
                            msg=payload,
                            digestmod=hashlib.sha256).digest()
    if sig != expected_sig:
        return False

    return data


def get_access_token_from_code(code, redirect_uri, app_id, app_secret):

    args = {
        "code": code, 
        "redirect_uri": redirect_uri,
        "client_id": app_id,
        "client_secret": app_secret,
    }
    # We would use GraphAPI.request() here, except for that the fact
    # that the response is a key-value pair, and not JSON.
    # response = urllib2.urlopen("https://graph.facebook.com/oauth/access_token" +
    #                           "?" + urllib.parse.urlencode(args)).read().decode('utf-8')
    response = requests.get("https://graph.facebook.com/oauth/access_token" +
                              "?" + urllib.parse.urlencode(args)).json()
    # query_str = parse_qs(response)

    # print (query_str)
    if "access_token" in response:
        result = {"access_token": response["access_token"]}
        if "expires" in response:
            result["expires"] = response["expires"]
        return result
    else:
        # jsonResponse = json.loads(str(response))
        # response = json.loads(response)
        # encoding = response.info().get_content_charset('utf8')
        # data = json.loads(response.read().decode(encoding))
        return response


def get_app_access_token(app_id, app_secret):

    # Get an app access token
    args = {'grant_type': 'client_credentials',
            'client_id': app_id,
            'client_secret': app_secret}

    file = urllib2.urlopen("https://graph.facebook.com/oauth/access_token?" +
                           urllib.parse.urlencode(args))

    try:
        result = file.read().decode('utf-8').split("=")[1]
    except:
        result = ''
    file.close()

    return result


def auth_url(app_id, canvas_url, perms=None, **kwargs):
    url = "https://www.facebook.com/dialog/oauth?"
    kvps = {'client_id': app_id, 'redirect_uri': canvas_url}
    if perms:
        kvps['scope'] = ",".join(perms)
    kvps.update(kwargs)
    return url + urllib.parse.urlencode(kvps)
