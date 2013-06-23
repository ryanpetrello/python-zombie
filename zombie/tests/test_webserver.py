import urllib2
import urllib
from zombie.tests.webserver import WebServerTestCase


class TestServerTests(WebServerTestCase):
    """
    Test the TestServer to make sure it does what we want and avoid misterious
    problems during normal testing
    """
    def test_index(self):
        response = urllib2.urlopen(self.base_url)
        self.assertEqual(200, response.getcode())
        self.assertEqual(response.headers['Content-type'], 'text/html')
        self.assertIn('<title>Example</title>', response.read())

    def test_post_submit(self):
        data = {'my_input': 'my_value'}
        encoded_data = urllib.urlencode(data)
        response = urllib2.urlopen(self.base_url + 'submit', encoded_data)
        self.assertEqual(200, response.getcode())
        self.assertEqual(response.headers['Content-type'], 'text/html')
        self.assertIn('Submitted', response.read())

    def test_redirect(self):
        response = urllib2.urlopen(self.base_url + 'redirect')
        self.assertEqual(self.base_url, response.geturl())

    def test_not_found(self):
        with self.assertRaises(urllib2.HTTPError):
            response = urllib2.urlopen(self.base_url + 'not_found_asf')
