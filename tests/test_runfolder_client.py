
import unittest
from unittest.mock import mock
from unittest.mock import MagicMock

import requests

from runfolder_client import RunfolderClient


class RunfolderClientTestCase(unittest.TestCase):

    def setUp(self):
        hosts = ['http://host1:11', 'http://host2:22']
        mock_logger = MagicMock()
        self.runfolder_client = RunfolderClient(hosts=hosts, logger=mock_logger)

    class MockResponse():
        def text(self):
            return "{'test': 'this'}"

    def test_next_ready(self):
        with mock.object(requests, 'get', return_value=self.MockResponse()):
            res = self.runfolder_client.next_ready()
            self.assertDictEqual(res, {'response': {'test': 'this'}, 'requesturl': 'http://host1:11'})

