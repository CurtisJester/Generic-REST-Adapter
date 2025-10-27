from local_paths import LOGGING_PATH

from pathlib import Path
from typing import Dict
from logging import Logger, getLogger, basicConfig, DEBUG, INFO, WARNING, ERROR, CRITICAL

from requests.exceptions    import RequestException
from requests.packages      import urllib3
from requests               import Session, Request


"""
     + BASIC INFO
    This is a generic REST adapter that provides the ability to get general logging and HTTPS requests up and 
    running.
    
     + GENERAL USE
    There are get, post, put, and delete HTTPS methods given that utilize a generic "do" method that encapsulates
    basic error checking and logging.   
"""


class RestAdapter:
    def __init__(self, hostname: str, api_key: str, ver: str = '', ssl_verify: bool = True,
                 logger: Logger = None, log_file: str = None, log_level: str = "DEBUG"):
        """
        The init method for the RestAdapter class.
        :param hostname: The base hostname for the REST API service.
        :param api_key: The API key needed for the REST API service.
        :param ver: An optional version string for the REST API service.
        :param ssl_verify: A bool for whether to verify SSL certificates.
        :param logger: The logger to use for logging.
        :param log_file: The log file to use/create. Str, one of: [DEBUG, INFO, WARNING, ERROR, CRITICAL]
        """
        self.url = f"https://{hostname}/"
        self.session = Session()
        if ver:
            self.url += f"{ver}/"
        self._api_key = api_key
        self._ssl_verify = ssl_verify
        self._logger_config(log_level=log_level.upper(), logger=logger, log_file=log_file)
        if not ssl_verify:
            # noinspection PyUnresolvedReferences
            urllib3.disable_warnings()

    def _logger_config(self, log_level: str, logger: Logger = None, log_file: str = None):
        """
        Initialize the logger.
        :param logger: Logger, if one was passed in.
        :param log_file: The filename for the logs.
        """
        levels = {
            "DEBUG": DEBUG,
            "INFO": INFO,
            "WARNING": WARNING,
            "ERROR": ERROR,
            "CRITICAL": CRITICAL
        }

        if log_level not in levels.keys():
            raise ValueError("Invalid log level {}".format(log_level))

        self._logger = logger or getLogger(__name__)
        if not log_file:
            log_file = "panorama_adapter.log"
        full_path = LOGGING_PATH / Path(log_file)
        if not full_path.exists():
            full_path.touch()
        basicConfig(filename=full_path, format='%(asctime)s - %(levelname)s - %(message)s',
                            filemode='a', level=levels[log_level])

    def log(self, level: str, msg: str):
        # Reference the logging class definitions for the level(int) to str comparisons
        match level.upper():
            case "FATAL" | "critical":
                self._logger.log(level=50, msg=msg)
            case "ERROR":
                self._logger.log(level=40, msg=msg)
            case "WARNING":
                self._logger.log(level=30, msg=msg)
            case "INFO":
                self._logger.log(level=20, msg=msg)
            case "DEBUG":
                self._logger.log(level=10, msg=msg)
            case _:
                self._logger.log(level=0, msg=msg)

    def _do_logless(self, http_method: str, endpoint: str, ep_params: Dict):
        """Necessary because our logging config is just basic; no filter applied to Logger"""
        full_url = self.url+endpoint
        request = Request(method=http_method, url=full_url, headers=self.session.headers, params=ep_params)
        prepared_request = request.prepare()
        try:
             response = self.session.send(prepared_request)
        except RequestException as e:
            raise
        return response

    def _do(self, http_method: str, endpoint: str, ep_params: Dict = None, data: Dict = None):
        """
        Generic method to encapsulate HTTP requests.
        :param http_method: The given HTTP method.
        :param endpoint: The given endpoint.
        :param ep_params: The endpoint parameters.
        :param data: The given data.
        :return: Result class that contains the response status code, message and data.
        """
        full_url = self.url+endpoint
        log_params = [f"{key}: {value}" for key, value in ep_params.items()] if ep_params else []
        log_line_pre = f"method={http_method}, url={full_url}, params={log_params}"
        # print(log_line_pre)
        log_line_post = ', '.join((log_line_pre, "success={success}, status_code={status_code}, message={message}"))
        try:
            # Prepare the request and log the outcome
            self._logger.debug(msg=log_line_pre)
            request = Request(method=http_method, url=full_url, headers=self.session.headers, params=ep_params, json=data)
            prepared_request = request.prepare()
            response = self.session.send(prepared_request)
        except RequestException as e:
            self._logger.error(msg=(str(e)))
            raise

        # If successful, format a log line and pass the response fields to Result class for return object
        is_success = 299 >= response.status_code >= 200
        log_line = log_line_post.format(success=is_success,
                                        status_code=response.status_code,
                                        message=response.reason)
        if is_success:
            self._logger.debug(msg=log_line)
            return response
        self._logger.error(msg=log_line)
        return response


    """These are the methods that implement each HTTP method, utilizing the encapsulating _do method."""
    def get(self, endpoint: str, ep_params: Dict = None):
        return self._do(http_method='GET', endpoint=endpoint, ep_params=ep_params)

    def post(self, endpoint: str, ep_params: Dict = None, data: Dict = None):
        return self._do(http_method='POST', endpoint=endpoint, ep_params=ep_params, data=data)

    def put(self, endpoint: str, ep_params: Dict = None, data: Dict = None):
        return self._do(http_method='PUT', endpoint=endpoint, ep_params=ep_params, data=data)

    def delete(self, endpoint: str, ep_params: Dict = None):
        return self._do(http_method='DELETE', endpoint=endpoint, ep_params=ep_params)
