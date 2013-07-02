class ConnectionError(IOError):
    pass


class HTTPError(Exception):
    def __init__(self, message=None, status_code=None):
        super(HTTPError, self).__init__(message)
        self.status_code = status_code


class ServerError(Exception):
    pass