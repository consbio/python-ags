from ags.base import Properties
from base import ServiceDefinition


class DynamicDataWorkspaceDefinition(Properties):
    """DynamicDataWorkspaceDefinition"""

    def get_properties(self):
        data = super(DynamicDataWorkspaceDefinition, self).get_properties()
        data.update({
            'id': "id",
            'workspace_factory': "WorkspaceFactory",
            'workspace_connection': "workspaceConnection"
        })


class MapServerProperties(Properties):
    """MapServer properteries"""

    def get_properties(self):
        data = super(MapServerProperties, self).get_properties()
        data.update({
            'file_path': "filePath",
            'max_record_count': ("maxRecordCount", 500),
            'max_buffer_count': ("maxBufferCount", 100),
            'max_image_width': ("maxImageWidth", 2048),
            'max_image_height': ("maxImageHeight", 2048),
            'supported_image_return_types': "supportedImageReturnTypes",
            'is_cached': ("isCached", False),
            'ignore_cache': ("ignoreCache", False),
            'cache_on_demand': ("cacheOnDemand", False),
            'client_caching_allowed': ("clientCachingAllowed", True),
            'cache_dir': "cacheDir",
            'virtual_cache_dir': "virtualCacheDir",
            'output_dir': "outputDir",
            'virtual_output_dir': "virtualOutputDir",
            'connection_check_interval': ("connectionCheckInterval", 300),
            'schema_locking_enabled': ("schemaLockingEnabled", True),
            'max_domain_code_count': ("maxDomainCodeCount", 25000),
            'use_local_cache_dir': ("useLocalCacheDir", False),
            'antialiasing_mode': ("antialiasingMode", "NONE"),
            'text_antialiasing_mode': ("textAntialiasingMode", "FORCE"),
            'disable_identify_relates': ("disableIdentifyRelates", False),
            'enable_dynamic_layers': "enableDynamicLayers",
            'dynamic_data_workspaces': "dynamicDataWorkspaces",
            'has_static_data': "hasStaticData"
        })
        return data


class MapServerDefinition(ServiceDefinition):
    """MapServerDefinition"""

    def __init__(self, **kwargs):
        kwargs.update({
            'type': "MapServer",
            'capabilities': "Map,Query,Data",
            'properties': MapServerProperties()
        })
        super(MapServerDefinition, self).__init__(**kwargs)