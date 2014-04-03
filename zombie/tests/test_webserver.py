from zombie.compat import PY3, to_bytes
if PY3:
    from urllib.request import urlopen
    from urllib.parse import urlencode
    from urllib.error import HTTPError
else:
    from urllib2 import urlopen, HTTPError
    from urllib import urlencode
from zombie.tests.webserver import WebServerTestCase


class TestServerTests(WebServerTestCase):
    """
    Test the TestServer to make sure it does what we want and avoid misterious
    problems during normal testing
    """
    def test_index(self):
        response = urlopen(self.base_url)
        self.assertEqual(200, response.getcode())
        self.assertEqual(response.headers['Content-type'], 'text/html')
        self.assertIn('<title>Example</title>', str(response.read()))

    def test_post_submit(self):
        data = {'my_input': 'my_value'}
        encoded_data = to_bytes(urlencode(data))
        response = urlopen(self.base_url + 'submit', encoded_data)
        self.assertEqual(200, response.getcode())
        self.assertEqual(response.headers['Content-type'], 'text/html')
        self.assertIn('Submitted', str(response.read()))

    def test_redirect(self):
        response = urlopen(self.base_url + 'redirect')
        self.assertEqual(self.base_url, response.geturl())

    def test_not_found(self):
        with self.assertRaises(HTTPError):
            response = urlopen(self.base_url + 'not_found_asf')
