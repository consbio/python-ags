class ConnectionError(IOError):
    pass


class HTTPError(Exception):
    def __init__(self, message=None, status_code=None):
        super(HTTPError, self).__init__(message)
        self.status_code = status_code


class ServerError(Exception):
    def __init__(self, message=None, error=None):
        self.message = message
        self.error = error
        if message:
            super(ServerError, self).__init__(message)