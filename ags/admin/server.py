import json
import time

import requests
from requests.packages.urllib3 import encode_multipart_formdata
from requests.utils import to_key_val_list
from requests.exceptions import ConnectionError as _ConnectionError

from ags.admin.services.base import ServiceStatus
from ags.admin.services.mapserver import MapServerDefinition
from ags.admin.uploads import UploadItem
from paths import AGS_ADMIN_PATH_PATTERNS
from services.gp import GPServerDefinition
from services.base import ServiceDefinition, ServiceItemInfo
from ags.exceptions import HTTPError, ServerError, ConnectionError


class ServerAdmin(object):
    """A connection to an ArcGIS server admin."""

    def __init__(self, host, username, password, secure=False, admin_root="/arcgis/admin"):
        """
        Create a new connection to an ArcGIS server admin.

        :param host: ArcGIS server hostname
        :param username: Admin username
        :param password: Admin password
        :param secure: If True, requests will use HTTPS only
        :param admin_root: Root server admin path
        """

        self.host = host
        self.username = username
        self.password = password
        self.root = admin_root.rstrip('/')
        self.token = None
        self.token_expiration = None
        self.scheme = 'https' if secure else 'http'

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

    def _get_service_path(self, service_name, folder=''):
        return '/'.join((folder, service_name)).lstrip('/')

    def _get_path(self, name, **kwargs):
        kwargs['admin_root'] = self.root
        return AGS_ADMIN_PATH_PATTERNS[name] % kwargs

    def generate_token(self):
        """
        Generates a new token for this server. This should never need to be called directly, as the server will
        automatically generate a new token when necessary.
        """

        path = self._get_path("generate_token")
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

    def list_services(self, folder=''):
        """
        Returns two values. The first value is a list of folder names in the form
        [{'name': name, 'description': description}, ...], the second is a list of services in the form:
        [{'name': name, 'type': type, 'description': description}, ...]

        :param folder: folder within which to list services and subfolders.
        """

        response = self._get(self._get_path("list_services", folder=folder))
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

    def service_exists(self, service_name, service_type, folder=''):
        """
        Checks to see if the service exists on this server

        :param service_name: name of the service
        :param service_type: service type
        :param folder: folder path to service
        """

        try:
            self.get_service_status(service_name, service_type, folder)
            return True
        except HTTPError as e:
            if not e.status_code == 404:
                raise
        return False

    def create_folder(self, folder_name, description):
        """
        Creates a new folder on the ArcGIS server.

        :param folder_name: name of the folder to create
        :param description: description of the folder
        """

        data = {
            'folderName': folder_name,
            'description': description
        }
        self._post(self._get_path("create_folder"), data)

    def edit_folder(self, folder_name, description, web_encrypted=False):
        """
        Modifies the given folder description and "webEncrypted" property

        :param folder_name: the folder to modify
        :param description: updated description
        :param web_encrypted: sets the webEncrypted property of the folder

        """

        data = {
            'description': description,
            'webEncrypted': web_encrypted,
        }
        self._post(self._get_path("edit_folder", folder=folder_name), data)

    def delete_folder(self, folder_name):
        """
        Deletes the given folder and all services within it

        :param folder_name: the folder to delete
        """

        self._post(self._get_path("delete_folder", folder=folder_name))

    def get_service(self, service_name, service_type, folder=''):
        """
        Retrieves a service definition from this ArcGIS server.

        :param service_name: service name
        :param service_type: service type
        :param folder: folder path containing the service
        """

        response = self._get(self._get_path("get_service", service_path=self._get_service_path(service_name, folder),
                                           service_type=service_type))

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
        """
        Creates the given service on this ArcGIS server.

        :param service: service name
        :param folder: folder to create the service within (optional)
        """

        if folder:
            if folder[0] != "/":
                folder = "/" + folder
            path = self._get_path("create_service", folder=folder)
        else:
            path = self._get_path("create_service", folder="")
        data = {
            'service': json.dumps(service.get_data())
        }
        self._post(path, data)

    def edit_service(self, service, service_name, service_type, folder=''):
        """
        Modifies the given service on this ArcGIS server.

        :param service: service properties object
        :param service_name: service name
        :param service_type: service type
        :param folder: folder path containing the service

        """

        path = self._get_path("edit_service", service_path=self._get_service_path(service_name, folder),
                             service_type=service_type)
        data = {
            'service': json.dumps(service.get_data())
        }
        self._post(path, data)

    def get_service_item_info(self, service_name, service_type, folder=''):
        """
        Retrieves item info for the given service on this ArcGIS server.

        :param service_name: service name
        :param service_type: service type
        :param folder: folder path containing the service
        :return: service item information object
        """

        path = self._get_path("get_service_item_info", service_path=self._get_service_path(service_name, folder),
                             service_type=service_type)
        response = self._get(path)
        info = ServiceItemInfo()
        info.set_from_dictionary(response)
        return info

    def edit_service_item_info(self, info, service_name, service_type, folder=''):
        """
        Sets item info for the given service on this ArcGIS server.

        :param info: service item information object
        :param service_name: service name
        :param service_type: service type
        :param folder: folder path containing the service
        """

        path = self._get_path("edit_service_item_info", service_path=self._get_service_path(service_name, folder),
                             service_type=service_type)
        data = {
            'serviceItemInfo': json.dumps(info.get_data())
        }
        self._post(path, data, files={'thumbnail': ""})

    def get_service_status(self, service_name, service_type, folder=''):
        """
        Gets the status info for the given service on this ArcGIS server.

        :param service_name: service name
        :param service_type: service type
        :param folder: folder path containing the service
        """

        response = self._get(self._get_path("get_service_status",
                                           service_path=self._get_service_path(service_name, folder),
                                           service_type=service_type))
        status = ServiceStatus()
        status.set_from_dictionary(response)
        return status

    def start_service(self, service_name, service_type, folder=''):
        """
        Starts the specified service on this ArcGIS server.

        :param service_name: service name
        :param service_type: service type
        :param folder: folder path containing the service"""

        self._post(self._get_path("start_service", service_path=self._get_service_path(service_name, folder),
                                 service_type=service_type))

    def stop_service(self, service_name, service_type, folder=''):
        """
        Stops the specified service on this ArcGIS server.

        :param service_name: service name
        :param service_type: service type
        :param folder: folder path containing the service
        """

        self._post(self._get_path("stop_service", service_path=self._get_service_path(service_name, folder),
                                 service_type=service_type))

    def delete_service(self, service_name, service_type, folder=''):
        """
        Stops the specified service on this ArcGIS server.

        :param service_name: service name
        :param service_type: service type
        :param folder: folder path containing the service
        """

        self._post(self._get_path("delete_service", service_path=self._get_service_path(service_name, folder),
                                 service_type=service_type))

    def upload_item(self, file_or_path, description):
        """
        Uploads a file, provided as a path of a file-like object.

        :param file_or_path: file-like object or path to a file
        :param description: description of file
        """

        if isinstance(file_or_path, basestring):
            file_obj = open(file_or_path, 'rb')
        else:
            file_obj = file_or_path

        path = self._get_path("upload_item")
        response = self._post(path, data={'description': description}, files={'itemFile': file_obj})
        item = UploadItem()
        item.set_from_dictionary(response['item'])
        return item