from socket import error as SocketError
import os
import subprocess
import signal
import threading
import time
import atexit
import random
import sys

from zombie.proxy.client import ZombieProxyClient

__all__ = ['ZombieProxyServer']
__proxy_instances__ = []


class PipeWorker(threading.Thread):
    """
    A thread that monitors and redirects node.js stdout and stderr to the
    parent process console.
    """

    def __init__(self, pipe):
        super(PipeWorker, self).__init__()
        self.pipe = pipe
        self.setDaemon(True)

    def __worker__(self, pipe):
        while True:
            line = pipe.readline()
            if line:
                sys.stdout.write(line)
            else:
                break

    def run(self):
        try:
            self.__worker__(self.pipe)
        except Exception as e:
            try:
                sys.stdout.write(e)
            except:  # pragma: nocover
                pass


class ZombieProxyServer(object):

    def __init__(self, socket=None, wait=True):
        """
        Spawns a node.js subprocess that listens on a TCP socket.
        A ZombieProxyClient streams data to the server, which
        evaluates it as Javascript, passes it on to a Zombie.js
        Browser object, and returns the results.

        :param socket: a (random, by default) filepath representing the
                       intended TCP socket location
        :param wait: when True, wait until the node.js subprocess is responsive
                    via the specified TCP socket.
        """
        socket = socket or '/tmp/zombie-%s.sock' % random.randint(0, 10000)

        self.socket = socket
        #
        # Spawn the node proxy server in a subprocess.
        # This is a simple socket server that listens for data,
        # evaluates it as Javascript, and passes the eval'ed
        # input to a Zombie.js Browser object.
        #
        args = ['env', 'node', self.__proxy_path__(), self.socket]
        self.child = subprocess.Popen(
            args,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )
        self.child.stdin.close()

        if wait:
            # Wait until we can ping the node.js server
            client = ZombieProxyClient(socket)
            retries = 30
            while True:
                retries -= 1
                if retries < 0:  # pragma: nocover
                    raise RuntimeError(
                        "The proxy server has not replied within 3 seconds."
                    )
                try:
                    assert client.ping() == 'pong'
                except (SocketError, AssertionError):
                    pass
                else:
                    break
                time.sleep(.1)

        global __proxy_instances__
        __proxy_instances__.append((self.child, self.socket))

        #
        # Start a thread to monitor and redirect the
        # subprocess stdout and stderr to the console.
        #
        PipeWorker(self.child.stdout).start()

    @classmethod
    def __proxy_path__(self):
        return os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'server.js'
        )


# When this process ends, ensure all node subprocesses terminate
def __kill_node_processes__():  # pragma: nocover
    for child, socket in __proxy_instances__:
        from os import path
        if hasattr(child, 'kill'):
            child.kill()

        # Cleanup the closed socket
        if path.exists(socket):
            from os import remove
            remove(socket)
atexit.register(__kill_node_processes__)
signal.signal(signal.SIGTERM, lambda signum, stack_frame: exit(1))
signal.signal(signal.SIGINT, lambda signum, stack_frame: exit(1))
