import subprocess
import threading
import time
import atexit
import os
import random
import sys

class PipeWorker(threading.Thread):

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
        except Exception, e:
            sys.stdout.write(e)


class ZombieProxyServer(object):
    """
    Spawns a node.js subprocess that listens on a TCP socket.
    A ZombieProxyClient streams data to the server, which
    evaluates it as Javascript, passes it on to a Zombie.js
    Browser object, and returns the results.
    """

    def __init__(self, socket=None, wait=True):
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
            retries = 100
            while not os.path.exists(socket):
                retries -= 1
                if retries < 0:
                    raise RuntimeError("Server has not been started for 10 seconds.")
                time.sleep(.1)


        #
        # Start a thread to monitor and redirect the
        # subprocess stdout and stderr to the console.
        #
        PipeWorker(self.child.stdout).start()

        # When this process ends, clean up the node subprocess
        atexit.register(self.kill)

    @classmethod
    def __proxy_path__(self):
        path = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(path, 'server.js')

    def kill(self):
        if self.child:
            self.child.kill()
            self.child = None

        # Cleanup the closed socket
        if os.path.exists(self.socket):
            os.remove(self.socket)
