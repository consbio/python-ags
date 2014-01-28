import json
from time import sleep
import requests


class GPError(Exception):
    pass


class GPMessage(object):
    INFORMATIVE = 1
    WARNING = 2
    ERROR = 3
    EMPTY = 4
    ABORT = 5

    def __init__(self, type, message):
        self.type = type
        self.message = message

    def __repr__(self):
        if self.type == self.INFORMATIVE:
            return "(Message) %s" % self.message
        else:
            return "(Error) %s" % self.message

    def __str__(self):
        return str(self.message)

    def __unicode__(self):
        return unicode(self.message)


class GPResult(object):
    def __init__(self, name, type, value):
        self.name = name
        self.type = type
        self.value = value


class GPTask(object):
    NOT_SUBMITTED = 0
    WAITING = 1
    SUBMITTED = 2
    RUNNING = 3
    SUCCEEDED = 4
    FAILED = 5
    CANCELLING = 6
    CANCELLED = 7

    def __init__(self, url, parameters={}):
        self.url = url
        self.parameters = parameters
        self.output_sr = None
        self.process_sr = None
        self.return_z = False
        self.return_m = False

        self.status = self.NOT_SUBMITTED
        self.messages = []
        self.job_id = None

    def submit_job(self, blocking=False):
        """Submit the GP task for processing. If blocking=True, this call will block until the job is complete."""

        data = {
            'f': "json",
            'returnZ': str(self.return_z).lower(),
            'returnM': str(self.return_m).lower()
        }
        data.update(self.parameters)
        if self.output_sr:
            data['env:outputSR'] = self.output_sr
        if self.process_sr:
            data['env:processSR'] = self.process_sr

        url = "%s/submitJob" % self.url
        r = requests.post(url, data=data)
        if 200 >= r.status_code < 300:
            try:
                data = json.loads(r.text)
            except ValueError:
                raise GPError("Server did not return a valid JSON response")
            try:
                self.job_id = data['jobId']
            except KeyError:
                raise GPError("Server response is missing 'jobId' parameter")
            return self.poll(blocking=blocking)
        else:
            raise GPError("Server returned HTTP %d" % r.status_code)

    def poll(self, blocking=False):
        """Poll job status. If blocking=True, this call will continue to poll (and block) until the job is complete."""

        url = "%s/jobs/%s?f=json" % (self.url, self.job_id)

        while True:
            r = requests.get(url)
            if 200 >= r.status_code < 300:
                try:
                    data = json.loads(r.text)
                except ValueError:
                    raise GPError("Server did not return a valid JSON response")
                try:
                    status = data['jobStatus']
                except KeyError:
                    raise GPError("Server response is missing 'jobStatus' parameter")
                if status in ESRI_JOB_STATUSES:
                    self.status = ESRI_JOB_STATUSES[status]
                else:
                    raise GPError("Unrecognized job status: %s" % status)
                self._populate_messages(data.get('messages', None))
                self._populate_results(data.get('results', None))
                if not blocking or self.status in (self.SUCCEEDED, self.FAILED, self.CANCELLED):
                    return self.status
                else:
                    sleep(1)
                    continue
            else:
                raise GPError("Server returned HTTP %d" % r.status_code)

    def execute(self):
        """Executes a synchronous task."""

        data = {
            'f': "json",
            'returnZ': str(self.return_z).lower(),
            'returnM': str(self.return_m).lower()
        }
        data.update(self.parameters)
        if self.output_sr:
            data['env:outputSR'] = self.output_sr
        if self.process_sr:
            data['env:processSR'] = self.process_sr
        url = "%s/execute" % self.url
        r = requests.post(url, data=data)
        if 200 >= r.status_code < 300:
            try:
                data = json.loads(r.text)
            except ValueError:
                raise GPError("Server did not return a valid JSON response")
            if data.get("error", None):
                self.status = self.FAILED
                self._populate_messages(data.get('messages', None))
                return self.status
            self.status = self.SUCCEEDED
            self._populate_messages(data.get('messages', None))
            self._populate_results(data.get('results', None))
            return self.status
        else:
            raise GPError("Server returned HTTP %d" % r.status_code)

    def _populate_messages(self, messages):
        self.messages = []
        if isinstance(messages, list):
            for message in messages:
                if isinstance(message, dict) and 'type' in message and 'description' in message:
                    if message['type'] in ESRI_MESSAGE_TYPES:
                        type = ESRI_MESSAGE_TYPES[message['type']]
                    else:
                        continue
                    self.messages.append(GPMessage(type, message['description']))

    def _populate_results(self, results):
        self.results = {}
        if isinstance(results, list):
            for result in results:
                if isinstance(result, dict) and 'paramName' in result and 'dataType' in result:
                    self.results[result['paramName']] = GPResult(
                        result['paramName'],
                        result['dataType'],
                        result['value']
                    )


ESRI_JOB_STATUSES = {
    'esriJobWaiting': GPTask.WAITING,
    'esriJobSubmitted': GPTask.SUBMITTED,
    'esriJobExecuting': GPTask.RUNNING,
    'esriJobSucceeded': GPTask.SUCCEEDED,
    'esriJobFailed': GPTask.FAILED,
    'esriJobCancelling': GPTask.CANCELLING,
    'esriJobCancelled': GPTask.CANCELLED
}

ESRI_MESSAGE_TYPES = {
    'esriJobMessageTypeInformative': GPMessage.INFORMATIVE,
    'esriJobMessageTypeWarning': GPMessage.WARNING,
    'esriJobMessageTypeError': GPMessage.ERROR,
    'esriJobMessageTypeEmpty': GPMessage.EMPTY,
    'esriJobMessageTypeAbort': GPMessage.ABORT,
    'esriGPMessageTypeInformative': GPMessage.INFORMATIVE,
    'esriGPMessageTypeWarning': GPMessage.WARNING,
    'esriGPMessageTypeError': GPMessage.ERROR,
    'esriGPMessageTypeEmpty': GPMessage.EMPTY,
    'esriGPMessageTypeAbort': GPMessage.ABORT
}