from pythonzombie.proxy.server      import ZombieProxyServer
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


class TestServerSpawn(TestCase):

    def setUp(self):
        super(TestServerSpawn, self).setUp()
        self.server = ZombieProxyServer()

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
