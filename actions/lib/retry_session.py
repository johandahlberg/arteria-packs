import requests
from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter


class RetrySession():

    HTTP_ADAPTER_MAX_RETRIES = 5
    HTTP_ADAPTER_BACKOFF_FACTOR = 1.0

    def __init__(self, max_retries=None, backoff_factor=None):
        s = requests.Session()

        self.retries = Retry(total=max_retries or RetrySession.HTTP_ADAPTER_MAX_RETRIES,
                             backoff_factor=backoff_factor or RetrySession.HTTP_ADAPTER_BACKOFF_FACTOR,
                             method_whitelist=False)

        self.adapter = HTTPAdapter(max_retries=self.retries)

        # Support both http and https
        s.mount('http://', self.adapter)
        s.mount('https://', self.adapter)

        self.session = s

    # Wrapper for requests.post
    def post(self, url, data=None, json=None, **kwargs):
        return self.session.post(url, data, json, **kwargs)

