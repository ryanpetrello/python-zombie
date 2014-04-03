import os
from zombie.compat import TestCase, PY3
if PY3:
    from socketserver import UnixStreamServer, StreamRequestHandler
else:
    from SocketServer import UnixStreamServer, StreamRequestHandler
import threading

try:
    from json import loads, dumps
except ImportError:
    from simplejson import loads, dumps  # noqa
import fudge

from zombie.proxy.client import (
    encode,
    encode_args,
    decode,
    Element,
    NodeError,
    ZombieServerConnection,
    ZombieProxyClient)
from zombie.proxy.server import ZombieProxyServer
from zombie.tests.webserver import WebServerTestCase


class EncodeTests(TestCase):
    def test_json(self):
        obj = lambda: 1
        obj.json = "myjson"
        self.assertEqual("myjson", encode(obj))

    def test_json_method(self):
        obj = lambda: 1
        obj.__json__ = lambda: "anotherjson"
        self.assertEqual("anotherjson", encode(obj))

    def test_asis(self):
        obj = [1, 2]
        self.assertEqual("[1, 2]", encode(obj))


class EncodeArgsTests(TestCase):
    def test_none(self):
        self.assertEqual('', encode_args(None))

    def test_empty(self):
        self.assertEqual('', encode_args([]))

    def test_arguments(self):
        self.assertEqual('"one", "two"', encode_args(['one', 'two']))

    def test_arguments_extra(self):
        self.assertEqual('"one", ', encode_args(['one'], True))


class DecodeTests(TestCase):
    def test_none(self):
        self.assertEqual(None, decode(None))

    def test_something(self):
        self.assertEqual([1], decode("[1]"))


class ElementTests(TestCase):
    def test_index(self):
        self.assertEqual(15, Element(15).index)

    def test_json(self):
        self.assertEqual("ELEMENTS[15]", Element(15).json)

    def test_str(self):
        self.assertEqual("ELEMENTS[15]", str(Element(15)))


class EchoHandler(StreamRequestHandler):
    def handle(self):
        self.wfile.write(self.rfile.readline())


class EchoServer(threading.Thread):
    def __init__(self, address):
        super(EchoServer, self).__init__()
        self.daemon = True
        self.server = UnixStreamServer(address, EchoHandler)

    def run(self):
        self.server.handle_request()

    def stop(self):
        self.server.shutdown()


class ZombieServerConnectionTests(TestCase):
    address = '/tmp/testing-unix-server'

    def cleanup(self):
        if os.path.exists(self.address):
            os.remove(self.address)

    def setUp(self):
        self.cleanup()
        self.server = EchoServer(self.address)
        self.server.start()
        self.connection = ZombieServerConnection(self.address)

    def tearDown(self):
        self.cleanup()

    def test_send(self):
        res = self.connection.send('Hello world!\n')
        self.assertEqual('Hello world!\n', res)


class ZombieProxyClientTests(WebServerTestCase):
    def setUp(self):
        super(ZombieProxyClientTests, self).setUp()
        # Note, As a singleton so it will be created once, not in every test.
        self.server = ZombieProxyServer()
        self.client = ZombieProxyClient(self.server.socket)

    def tearDown(self):
        super(ZombieProxyClientTests, self).tearDown()

    def test_simple_json(self):
        obj = {
            'foo': 'bar',
            'test': 500
        }
        self.assertEqual(obj, self.client.json(obj))

    def test_malformed_command(self):
        with self.assertRaises(NodeError):
            self.client.json("banana")

    def test_nowait(self):
        self.assertEqual('Test', self.client.nowait("result = 'Test';"))

    def test_wait(self):
        self.client.wait('browser.visit', self.base_url)

    def test_wait_error(self):
        with self.assertRaises(NodeError):
            self.client.wait('browser.visit', self.base_url + 'notfound')

    def test_ping(self):
        self.assertEqual("pong", self.client.ping())

    def test_cleanup(self):
        client = self.client
        self.assertEqual(1, client.json('browser.testing = 1'))
        client.cleanup()
        self.assertFalse(client.json('"testing" in browser'))

    def test_create_element(self):
        client = self.client
        client.wait('browser.visit', self.base_url)
        self.assertEqual(
            0,
            client.create_element('browser.query', ('form',)).index)
        self.assertEqual(
            1,
            client.create_element('browser.query', ('form',)).index)

    def test_create_element_attribute(self):
        client = self.client
        client.wait('browser.visit', self.base_url)
        self.assertEqual(
            0, client.create_element('browser.html').index)

    def test_create_elements(self):
        client = self.client
        client.wait('browser.visit', self.base_url)
        res = client.create_elements('browser.queryAll', ('input', ))
        self.assertEqual(list(range(6)), [x.index for x in res])
