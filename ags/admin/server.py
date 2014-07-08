import json
import time
import requests
from requests.packages.urllib3 import encode_multipart_formdata
from requests.utils import to_key_val_list
from ags.admin.services.base import ServiceStatus
from ags.admin.services.mapserver import MapServerDefinition
from ags.admin.uploads import UploadItem
from paths import AGS_ADMIN_PATH_PATTERNS
from services.gp import GPServerDefinition
from services.base import ServiceDefinition, ServiceItemInfo
from ags.exceptions import HTTPError, ServerError, ConnectionError
from requests.exceptions import ConnectionError as _ConnectionError


class ServerAdmin(object):
    """A connection to an ArcGIS server admin."""

    def __init__(self, host, username, password, secure=False, admin_root="/arcgis/admin"):
        """
        Create a new connection to an ArcGIS server admin.
        :param host: ArcGIS server hostname
        :param username: Admin username
        :param password: Admin password
        :param secure: If True, requests will use HTTPS only
        :param admin_root: Root server admin path (no trailing slash)
        """

        self.host = host
        self.username = username
        self.password = password
        self.root = admin_root
        self.token = None
        self.token_expiration = None

        if secure:
            self.scheme = "https"
        else:
            self.scheme = "http"

    def _post(self, path, data={}, files=None, headers={}, multipart=False):
        if not self.token or self.token_expiration >= time.time():
            self.generate_token()

        try:
            url, data = self._prepare_request(path, data)
            if multipart and not files:
                fields = to_key_val_list(data)
                new_fields = []
                for field, val in fields:
                    if isinstance(val, basestring) or not hasattr(val, '__iter__'):
                        val = [val]
                    for v in val:
                        if v is not None:
                            new_fields.append(
                                (field.decode('utf-8') if isinstance(field, bytes) else field,
                                 v.encode('utf-8') if isinstance(v, str) else v))
                body, content_type = encode_multipart_formdata(new_fields)
                headers.update({
                    'Content-type': content_type
                })
                response = requests.post(url, data=body, headers=headers)
            else:
                response = requests.post(url, data=data, files=files, headers=headers)
            return self._process_response(url, response)
        except _ConnectionError, e:
            raise ConnectionError(e.message)

    def _get(self, path, data={}, headers={}):
        if not self.token or self.token_expiration >= time.time():
            self.generate_token()

        url, data = self._prepare_request(path, data)
        return self._process_response(url, requests.get(url, params=data, headers=headers))

    def _prepare_request(self, path, data):
        data.update({
            'f': "json",
            'token': self.token
        })
        return "%s://%s%s" % (self.scheme, self.host, path), data

    def _process_response(self, url, response):
        """Internal method to validate and deserialize server response."""

        if response.status_code >= 300 or response.status_code < 200:
            raise HTTPError("Error loading URL %s. The response was %d (%s)" %
                            (url, response.status_code, response.reason), response.status_code)
        elif response.content:
            try:
                data = json.loads(response.content, strict=False)
                if data.get('status', None) == "error":
                    if data.get('code', None):
                        raise HTTPError("Error loading URL %s. The response was %d (%s)" % (url, data['code'],
                                        ",".join(data['messages'])), data['code'])
                    raise ServerError("ArcGIS server response indicates error: %s" % data['messages'])
                return data
            except ValueError:
                raise ServerError("Error parsing response from server: %s" % response.content)

    def get_path(self, name, **kwargs):
        kwargs['admin_root'] = self.root
        return AGS_ADMIN_PATH_PATTERNS[name] % kwargs

    def generate_token(self):
        """
        Generates a new token for this server. This should never need to be called directly, as the server will
        automatically generate a new token when necessary.
        """

        path = self.get_path("generate_token")
        data = {
            'username': self.username,
            'password': self.password,
            'client': "requestip",
            'f': "json"
        }
        url = "%s://%s%s" % (self.scheme, self.host, path)
        response = self._process_response(url, requests.post(url, data=data))
        try:
            self.token, self.token_expiration = response['token'], response['expires']
        except KeyError:
            raise ValueError("ArcGIS server returned an invalid generate token resopnse: %s" % str(response))

    def list_services(self, folder="/"):
        """
        Returns two values. The first value is a list of folder names in the form
        [{'name': name, 'description': description}, ...], the second is a list of services in the form:
        [{'name': name, 'type': type, 'description': description}, ...]
        """

        if folder[0] != "/":
            folder = "/" + folder
        path = self.get_path("list_services", folder=folder)
        response = self._get(path)
        folders = []
        services = []

        for folder in response.get('foldersDetail', []):
            folders.append({
              'name': folder['folderName'],
              'description': folder['description']
            })
        for service in response['services']:
            services.append({
                'name': service['serviceName'],
                'type': service['type'],
                'description': service['description']
            })

        return folders, services

    def service_exists(self, service_name, service_type, folder=None):
        """Checks to see if the service exists on this server"""

        try:
            self.get_service_status(service_name, service_type, folder)
            return True
        except HTTPError as e:
            if not e.status_code == 404:
                raise
        return False

    def create_folder(self, name, description):
        """Creates a new folder on the ArcGIS server"""

        path = self.get_path("create_folder")
        data = {
            'folderName': name,
            'description': description
        }
        self._post(path, data)

    def edit_folder(self, folder_name, description, web_encrypted=False):
        """Modifies the given folder description and "webEncrypted" property"""

        path = self.get_path("edit_folder", folder=folder_name)
        data = {
            'description': description,
            'webEncrypted': web_encrypted,
        }
        self._post(path, data)

    def delete_folder(self, folder_name):
        """Deletes the given folder and all services within it"""

        path = self.get_path("delete_folder", folder=folder_name)
        self._post(path)

    def get_service(self, service_name, service_type, folder=None):
        """Retrieves a service definition from this ArcGIS server"""

        if folder:
            path = self.get_path("get_service", service_path="%s/%s" % (folder, service_name),
                                 service_type=service_type)
        else:
            path = self.get_path("get_service", service_path=service_name, service_type=service_type)

        response = self._get(path)

        if service_type == "GPServer":
            service = GPServerDefinition(service_name=service_name)
        elif service_type == "MapServer":
            service = MapServerDefinition(service_name=service_name)
        else:
            service = ServiceDefinition(
                service_name=service_name,
                type=service_type
            )

        service.set_from_dictionary(response)
        return service

    def create_service(self, service, folder=None):
        """Creates the given service on this ArcGIS server."""

        if folder:
            if folder[0] != "/":
                folder = "/" + folder
            path = self.get_path("create_service", folder=folder)
        else:
            path = self.get_path("create_service", folder="")
        data = {
            'service': json.dumps(service.get_data())
        }
        self._post(path, data)

    def edit_service(self, service, service_name, service_type, folder=None):
        """Modifies the given service on this ArcGIS server."""

        if folder:
            path = self.get_path("edit_service", service_path="%s/%s" % (folder, service_name),
                                 service_type=service_type)
        else:
            path = self.get_path("edit_service", service_path=service_name, service_type=service_type)
        data = {
            'service': json.dumps(service.get_data())
        }
        self._post(path, data)

    def get_service_item_info(self, service_name, service_type, folder=None):
        """Retrieves item info for the given service on this ArcGIS server."""

        if folder:
            path = self.get_path("get_service_item_info", service_path="%s/%s" % (folder, service_name),
                                 service_type=service_type)
        else:
            path = self.get_path("get_service_item_info", service_path=service_name, service_type=service_type)
        response = self._get(path)
        info = ServiceItemInfo()
        info.set_from_dictionary(response)
        return info

    def edit_service_item_info(self, info, service_name, service_type, folder=None):
        """Sets item info for the given service on this ArcGIS server."""

        if folder:
            path = self.get_path("edit_service_item_info", service_path="%s/%s" % (folder, service_name),
                                 service_type=service_type)
        else:
            path = self.get_path("edit_service_item_info", service_path=service_name, service_type=service_type)
        data = {
            'serviceItemInfo': json.dumps(info.get_data())
        }
        self._post(path, data, files={'thumbnail': ""})

    def get_service_status(self, service_name, service_type, folder=None):
        if folder:
            path = self.get_path("get_service_status", service_path="%s/%s" % (folder, service_name),
                                 service_type=service_type)
        else:
            path = self.get_path("get_service_status", service_path=service_name, service_type=service_type)
        response = self._get(path)
        status = ServiceStatus()
        status.set_from_dictionary(response)
        return status

    def start_service(self, service_name, service_type, folder=None):
        """Starts the specified service on this ArcGIS server."""

        if folder:
            path = self.get_path("start_service", service_path="%s/%s" % (folder, service_name),
                                 service_type=service_type)
        else:
            path = self.get_path("start_service", service_path=service_name, service_type=service_type)
        self._post(path)

    def stop_service(self, service_name, service_type, folder=None):
        """Stops the specified service on this ArcGIS server."""

        if folder:
            path = self.get_path("stop_service", service_path="%s/%s" % (folder, service_name),
                                 service_type=service_type)
        else:
            path = self.get_path("stop_service", service_path=service_name, service_type=service_type)
        self._post(path)

    def delete_service(self, service_name, service_type, folder=None):
        """Stops the specified service on this ArcGIS server."""

        if folder:
            path = self.get_path("delete_service", service_path="%s/%s" % (folder, service_name),
                                 service_type=service_type)
        else:
            path = self.get_path("delete_service", service_path=service_name, service_type=service_type)
        self._post(path)

    def upload_item(self, file_or_path, description):
        """Uploads a file, provided as a path of a file-like object."""

        if isinstance(file_or_path, basestring):
            file_obj = open(file_or_path, 'rb')
        else:
            file_obj = file_or_path

        path = self.get_path("upload_item")
        response = self._post(path, data={'description': description}, files={'itemFile': file_obj})
        item = UploadItem()
        item.set_from_dictionary(response['item'])
        return item