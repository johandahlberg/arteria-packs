import mock
from st2tests.base import BaseActionTestCase
from lib.retry_session import RetrySession


class TestRetrySession(BaseActionTestCase):
    action_cls = RetrySession

    class MockPostResponse:
        def __init__(self, content, status_code=200):
            self.content = content
            self.status_code = status_code

    def test_retry_values(self):
        rt = RetrySession(8, 0.2)
        self.assertEqual(rt.retries.total, 8)
        self.assertEqual(rt.retries.backoff_factor, 0.2)

    def test_default_retry_values(self):
        rt = RetrySession()
        self.assertTrue(type(RetrySession.HTTP_ADAPTER_MAX_RETRIES) is int)
        self.assertEqual(rt.retries.total, RetrySession.HTTP_ADAPTER_MAX_RETRIES)
        self.assertTrue(type(RetrySession.HTTP_ADAPTER_BACKOFF_FACTOR) is float)
        self.assertEqual(rt.retries.backoff_factor, RetrySession.HTTP_ADAPTER_BACKOFF_FACTOR)

    def test_adapters(self):
        rt = RetrySession()
        self.assertIs(rt.adapter.max_retries, rt.retries)
        self.assertIs(rt.session.get_adapter("http://"), rt.adapter)
        self.assertIs(rt.session.get_adapter("https://"), rt.adapter)

    def test_allows_all_methods(self):
        rt = RetrySession()
        self.assertFalse(rt.retries.method_whitelist)

    def test_post(self):
        rt = RetrySession()
        fake_url = 'http://foo.bar/post'
        fake_body = {'foo': 'bar'}
        fake_kwargs = {'auth': {'foo', 'bar'}}
        mock_response = TestRetrySession.MockPostResponse("foo")

        with mock.patch.object(
            rt.session,
            'post',
            return_value=mock_response
        ) as post_mock:
            res = rt.post(fake_url, fake_body, fake_kwargs)
            post_mock.assert_called_with(fake_url, fake_body, fake_kwargs)
            self.assertIs(res, mock_response)
