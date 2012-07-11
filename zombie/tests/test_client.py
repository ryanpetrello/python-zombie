from unittest import TestCase

try:
    from json import loads, dumps
except ImportError:
    from simplejson import loads, dumps  # noqa
import fudge

from zombie.proxy.server import ZombieProxyServer
from zombie.proxy.client import ZombieProxyClient
from zombie.compat import StringIO


class FakeNode(object):
    def __json__(self):
        return 'ENCODED'


class FakePopen(object):

    stdin = StringIO()
    stdout = StringIO()


class TestServerCommunication(TestCase):

    def setUp(self):
        super(TestServerCommunication, self).setUp()
        self.server = ZombieProxyServer()
        self.client = ZombieProxyClient(self.server.socket)

    def tearDown(self):
        super(TestServerCommunication, self).tearDown()
        fudge.clear_expectations()

    def test_encode(self):
        foo = {
            'foo': 'bar'
        }
        self.client.__encode__(foo) == dumps(foo)

        self.client.__encode__(FakeNode()) == 'ENCODED'

    def test_decode(self):
        foo = dumps({
            'foo': 'bar'
        })
        self.client.__decode__(foo) == loads(foo)

    def test_simple_send(self):
        self.client.send(
            "stream.end()"
        )

    def test_simple_json(self):
        obj = {
            'foo': 'bar',
            'test': 500
        }
        assert self.client.json(obj) == obj

    @fudge.with_fakes
    def test_simple_wait(self):

        js = """
        try {
            browser.visit("%s", function(err, browser){
                if (err)
                    stream.end(JSON.stringify(err.stack));
                else
                    stream.end();
            });
        } catch (err) {
            stream.end(JSON.stringify(err.stack));
        }
        """ % 'http://example.com'

        with fudge.patched_context(
            ZombieProxyClient,
            'send',
            (
                fudge.Fake('send', expect_call=True).with_args(js)
            )
        ):
            self.client.wait('visit', 'http://example.com')

    @fudge.with_fakes
    def test_wait_without_arguments(self):

        js = """
        try {
            browser.wait(function(err, browser){
                if (err)
                    stream.end(JSON.stringify(err.stack));
                else
                    stream.end();
            });
        } catch (err) {
            stream.end(JSON.stringify(err.stack));
        }
        """

        with fudge.patched_context(
            ZombieProxyClient,
            'send',
            (
                fudge.Fake('send', expect_call=True).with_args(js)
            )
        ):
            self.client.wait('wait')
