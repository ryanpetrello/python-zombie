from unittest import TestCase
import subprocess
import os

import fudge

from zombie.proxy.server import ZombieProxyServer, proxy_path
from zombie.compat import StringIO


class FakeNode(object):
    def __json__(self):
        return 'ENCODED'


class FakePopen(object):

    stdin = StringIO()
    stdout = StringIO()


class TestServerSpawn(TestCase):

    def setUp(self):
        super(TestServerSpawn, self).setUp()
        self.server = ZombieProxyServer()

    def tearDown(self):
        super(TestServerSpawn, self).tearDown()
        fudge.clear_expectations()

    @property
    def _args(self):
        return [
            'env',
            'node',
            proxy_path,
            '/tmp/zombie.sock'
        ]

    @fudge.with_fakes
    def test_process_spawn(self):
        with fudge.patched_context(
            subprocess,
            'Popen',
            (fudge.Fake('Popen').
                is_callable().
                with_args(
                    self._args,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT
                ).returns(FakePopen()))):
            ZombieProxyServer(socket='/tmp/zombie.sock', wait=False)

    @fudge.with_fakes
    def test_configurable_socket(self):
        args = [
            'env',
            'node',
            proxy_path,
            '/tmp/zombie-custom.sock'
        ]
        with fudge.patched_context(
            subprocess,
            'Popen',
            (fudge.Fake('Popen').
                is_callable().
                with_args(
                    args,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT
                ).returns(FakePopen()))):
            ZombieProxyServer(socket='/tmp/zombie-custom.sock', wait=False)

    @fudge.with_fakes
    def test_stdout_redirect_exception(self):

        fake = FakePopen()
        fake.stdout = None

        with fudge.patched_context(
            subprocess,
            'Popen',
            (fudge.Fake('Popen').
                is_callable().
                with_args(
                    self._args,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT
                ).
                returns(fake))):
            ZombieProxyServer(socket='/tmp/zombie.sock', wait=False)

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
        else:
            pass

        assert os.path.exists(self.server.socket)
