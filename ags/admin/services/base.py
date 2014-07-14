from ags.base import Properties


class ServiceDefinition(Properties):
    """Generic ServiceDefinition"""

    def get_properties(self):
        props = super(ServiceDefinition, self).get_properties()
        props.update({
            #Service Description Properties
            'service_name': "serviceName",
            'type': "type",
            'description': "description",
            'capabilities': ("capabilities", ""),
            'format': ("f", "json"),

            #Service Framework Properties
            'cluster_name': ("clusterName", "default"),
            'min_instances_per_node': ("minInstancesPerNode", 1),
            'max_instances_per_node': ("maxInstancesPerNode", 2),
            'max_wait_time': ("maxWaitTime", 60),
            'max_startup_time': ("maxStartupTime", 300),
            'max_idle_time': ("maxIdleTime", 1800),
            'max_usage_time': ("maxUsageTime", 600),
            'recycle_interval': ("recycleInterval", 24),
            'load_balancing': ("loadBalancing", "ROUND_ROBIN"),
            'isolation_level': ("isolationLevel", "HIGH"),

            #Service Type Properties
            'properties': ("properties", {}),

            #Extension Properties
            'extensions': ("extensions", []),

            #Undocumented Properties
            'enabled': ("enabled", True),
            'datasets': ("datasets", [])
        })
        return props


class ServiceItemInfo(Properties):
    """Service iteminfo"""

    def get_properties(self):
        props = super(ServiceItemInfo, self).get_properties()
        props.update({
            'culture': "culture",
            'name': "name",
            'thumbnail': "thumbnail",
            'guid': "guid",
            'catalog_path': "catalogpath",
            'snippet': "snippet",
            'description': "description",
            'summary': "summary",
            'title': "title",
            'tags': "tags",
            'type': "type",
            'text': "text",
            'type_keywords': "typekeywords",
            'documentation': "documentation",
            'url': "url",
            'data_last_modified_time': "datalastmodifiedtime",
            'extent': "extent",
            'spatial_reference': "spatialreference",
            'access_information': "accessInformation",
            "license_info": "licenseInfo"
        })
        return props


class ServiceExtension(Properties):
    """Service extension description"""

    def get_properties(self):
        props = super(ServiceExtension, self).get_properties()
        props.update({
            'type_name': "typeName",
            'capabilities': ("capabilities", ""),
            'enabled': ("enabled", False),
            'properties': ("properties", {})
        })
        return props


class ServiceStatus(Properties):
    """Service status information"""

    def get_properties(self):
        props = super(ServiceStatus, self).get_properties()
        props.update({
            'configured_state': "configuredState",
            'realtime_state': "realTimeState"
        })
        return props