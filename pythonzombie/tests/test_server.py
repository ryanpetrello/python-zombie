from pythonzombie.server    import ZombieProxyServer
from simplejson             import loads, dumps
from unittest               import TestCase

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


class TestServerSpawn(TestCase):

    def tearDown(self):
        super(TestServerSpawn, self).tearDown()
        fudge.clear_expectations()

    @fudge.with_fakes
    def test_process_spawn(self):

        args = ['env', 'node', ZombieProxyServer.__proxy_path__(), '/tmp/zombie.sock']

        with fudge.patched_context(
            subprocess,
            'Popen',
            (fudge.Fake('Popen').
                is_callable().
                with_args(
                    args,
                    stdin = subprocess.PIPE,
                    stdout = subprocess.PIPE,
                    stderr = subprocess.STDOUT
                ).
                returns(FakePopen()))
            ):
            ZombieProxyServer()

    @fudge.with_fakes
    def test_configurable_socket(self):

        args = ['env', 'node', ZombieProxyServer.__proxy_path__(), '/tmp/zombie-custom.sock']

        with fudge.patched_context(
            subprocess,
            'Popen',
            (fudge.Fake('Popen').
                    is_callable().
                    with_args(
                        args,
                        stdin = subprocess.PIPE,
                        stdout = subprocess.PIPE,
                        stderr = subprocess.STDOUT
                    ).
                    returns(FakePopen()))
            ):
            ZombieProxyServer(socket='/tmp/zombie-custom.sock')

    @fudge.with_fakes
    def test_stdout_redirect_exception(self):

        args = ['env', 'node', ZombieProxyServer.__proxy_path__(), '/tmp/zombie.sock']
        fake = FakePopen()
        fake.stdout = None

        with fudge.patched_context(
            subprocess,
            'Popen',
            (fudge.Fake('Popen').
                is_callable().
                with_args(
                    args,
                    stdin = subprocess.PIPE,
                    stdout = subprocess.PIPE,
                    stderr = subprocess.STDOUT
                ).
                returns(fake))
            ):
            ZombieProxyServer()


class TestServerCommunication(TestCase):
    
    def setUp(self):
        super(TestServerCommunication, self).setUp()
        self.server = ZombieProxyServer()

    def tearDown(self):
        super(TestServerCommunication, self).tearDown()
        fudge.clear_expectations()
        self.server.kill()

    def test_server_running(self):
        assert self.server.child is not None
        assert self.server.child.pid is not None

        #
        # Sending signal 0 will raise an OSError
        # exception if the process is not running,
        # and do nothing otherwise.
        #
        try:
            os.kill(self.server.child.pid, 0)
        except OSError:
            assert False
        else: pass

        assert os.path.exists('/tmp/zombie.sock')

    def test_server_kill_cleanup(self):
        self.server.kill() 
        assert os.path.exists('/tmp/zombie.sock') == False

    def test_encode(self):
        foo = {
            'foo': 'bar'
        }
        self.server.__encode__(foo) == dumps(foo)

        self.server.__encode__(FakeNode()) == 'ENCODED'

    def test_decode(self):
        foo = dumps({
            'foo': 'bar'
        })
        self.server.__decode__(foo) == loads(foo)

    def test_simple_send(self):
        self.server.send(
            "stream.end()"
        )

    def test_simple_json(self):
        obj = {
            'foo'   : 'bar',
            'test'  : 500
        }
        assert self.server.json(obj) == obj

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
            ZombieProxyServer,
            '__send__',
            (fudge.Fake('__send__', expect_call=True).
                with_args(js)
            )):

            self.server.wait('visit', 'http://example.com')

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
            ZombieProxyServer,
            '__send__',
            (fudge.Fake('__send__', expect_call=True).
                with_args(js)
            )):

            self.server.wait('wait')
