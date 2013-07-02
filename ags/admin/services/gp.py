from ags.base import Properties
from base import ServiceDefinition


class GPServerProperties(Properties):
    def get_properties(self):
        data = super(GPServerProperties, self).get_properties()
        data.update({
            'toolbox': "toolbox",
            'execution_type': ("executionType", 'asynchronous'),
            'result_map_server': ("resultMapServer", False),
            'maximum_records': ("maximum_records", 100),
            'show_messages': ("show_messages", False),
            'jobs_directory': "jobsDirectory",
            'jobs_virtual_directory': "jobsVirtualDirectory",
            'output_dir': "outputDir",
            'virtual_output_dir': "virtualOutputDir",
            'local_jobs_dir': ("localJobsDir", False)
        })
        return data


class GPServerDefinition(ServiceDefinition):
    def __init__(self, **kwargs):
        kwargs.update({
            'type': "GPServer",
            'properties': GPServerProperties()
        })
        super(GPServerDefinition, self).__init__(**kwargs)