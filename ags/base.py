class Properties(object):
    """Base class for organizing and serializing service/server/description properties."""

    _data = {}
    _attr_name_map = {}
    _ags_name_map = {}

    def __init__(self, **kwargs):
        self.__dict__['_data'] = {}
        self.__dict__['_attr_name_map'] = {}
        self.__dict__['_ags_name_map'] = {}
        for k, v in self.get_properties().iteritems():
            if isinstance(v, basestring):
                self.__dict__['_data'][k] = None
                self.__dict__['_attr_name_map'][k] = v
                self.__dict__['_ags_name_map'][v] = k
            else:
                self.__dict__['_data'][k] = v[1]
                self.__dict__['_attr_name_map'][k] = v[0]
                self.__dict__['_ags_name_map'][v[0]] = k

        for k, v in kwargs.iteritems():
            if k in self._data:
                self.__dict__['_data'][k] = v
            else:
                raise AttributeError("Service definition has no attribute %s" % k)

    def __getattr__(self, key):
        if key in self._data:
            return self._data[key]
        else:
            raise AttributeError("Service definition has no attribute %s" % key)

    def __setattr__(self, key, value):
        if key in self._data:
            self.__dict__['_data'][key] = value
        else:
            raise AttributeError("Service definition has no attribute %s" % key)

    def get_properties(self):
        """
        Returns a dictionary of service definition properties properties for this service with optional default values.
        For example::

            {
                'service_name': 'serviceName',
                'format': ('f', "json")  # Default value will be 'json'
            }

        """

        return {}

    def get_data(self):
        """Returns a dictionary representing this description."""

        data = {}
        for k, v in self._data.iteritems():
            key = self._attr_name_map[k]
            if isinstance(v, Properties):
                v = v.get_data()
            if isinstance(v, (list, tuple)):
                li = []
                for item in v:
                    if isinstance(item, Properties):
                        li.append(item.get_data())
                    else:
                        li.append(item)
                v = li
            if v is not None:
                data[key] = v
        return data

    def set_from_dictionary(self, d):
        """Set properties form a dictionary. Keys are expected to be the API name, not the Python name."""

        for k, v in d.iteritems():
            if k in self._ags_name_map:
                self._data[self._ags_name_map[k]] = v