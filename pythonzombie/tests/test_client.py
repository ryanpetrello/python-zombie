from pythonzombie.proxy.server      import ZombieProxyServer
from pythonzombie.proxy.client      import ZombieProxyClient
from simplejson                     import loads, dumps
from unittest                       import TestCase

import cStringIO
import fudge
import subprocess
import os

class FakeNode(object):
    def __json__(self):
        return 'ENCODED'


class FakePopen(object):

    stdin = cStringIO.StringIO()
    stdout = cStringIO.StringIO()

    def kill(self):
        pass


class TestServerCommunication(TestCase):
    
    def setUp(self):
        super(TestServerCommunication, self).setUp()
        self.server = ZombieProxyServer()
        self.client = ZombieProxyClient()

    def tearDown(self):
        super(TestServerCommunication, self).tearDown()
        fudge.clear_expectations()
        self.server.kill()

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
            'foo'   : 'bar',
            'test'  : 500
        }
        assert self.client.json(obj) == obj

    @fudge.with_fakes
    def test_simple_wait(self):

        js = """
        browser.visit("http://example.com", function(err, browser){
            if(err)
                stream.end(JSON.stringify(err.stack));
            else    
                stream.end();
        });
        """

        with fudge.patched_context(
            ZombieProxyClient,
            '__send__',
            (fudge.Fake('__send__', expect_call=True).
                with_args(js)
            )):

            self.client.wait('visit', 'http://example.com')

    @fudge.with_fakes
    def test_wait_without_arguments(self):

        js = """
        browser.wait(null, function(err, browser){
            if(err)
                stream.end(JSON.stringify(err.stack));
            else    
                stream.end();
        });
        """

        with fudge.patched_context(
            ZombieProxyClient,
            '__send__',
            (fudge.Fake('__send__', expect_call=True).
                with_args(js)
            )):

            self.client.wait('wait')
