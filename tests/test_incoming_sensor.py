
import mock

import requests
from st2tests.base import BaseSensorTestCase

from incoming_sensor import IncomingSensor


class IncomingSensorTestCase(BaseSensorTestCase):

    sensor_cls = IncomingSensor

    class MockResponse():
        def __init__(self):
            self.status_code = 200

        def json(self):
            return {'path': '/foo',
                    'host': 'test',
                    'link': 'http://test.url/status_link'}

    def test_poll(self):
        sensor = self.get_sensor_instance(config={'incoming_svc_urls':
                                                      [{'dest_folder': 'test',
                                                        'remote_user': 'test',
                                                        'url': 'http://test.url',
                                                        'user_key': 'test'}]})
        sensor.setup()
        with mock.patch.object(requests, 'get', return_value=self.MockResponse()) as mock_get:
            sensor.poll()
            mock_get.assert_called_once()
            self.assertTriggerDispatched(trigger='snpseq_packs.incoming_ready')
