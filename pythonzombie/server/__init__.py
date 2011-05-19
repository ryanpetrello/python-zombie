from simplejson import loads, dumps

import subprocess
import socket
import threading
import time
import atexit
import os


class PipeWorker(threading.Thread):

    def __init__(self, pipe):
        super(PipeWorker, self).__init__()
        self.pipe = pipe
        self.setDaemon(True)

    def __worker__(self, pipe):
        while True:
            line = pipe.readline()
            if line:
                print line
            else: break

    def run(self):
        try:
            self.__worker__(self.pipe)
        except Exception, e:
            print e


class ZombieProxyServer(object):

    process = None

    def __init__(self, socket='/tmp/zombie.sock'):
        print "Starting Zombie.js..."
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
            stdin  = subprocess.PIPE,
            stdout = subprocess.PIPE,
            stderr = subprocess.STDOUT
        )
        self.child.stdin.close()
        time.sleep(.5)

        #
        # Start a thread to monitor and redirect the
        # subprocess stdout and stderr to the console.
        #
        PipeWorker(self.child.stdout).start()

        # When this process ends, clean up the node subprocess
        atexit.register(self.kill)

    def __proxy_path__(self):
        path = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(path, 'server.js')

    def __send__(self, js):
        # Establish a socket connection to the Zombie.js proxy server
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.connect(self.socket)

        # Send Zombie.js API calls, followed by a stream.end() call.
        s.send("%s" % js)

        # Read the response
        response = []
        while True:
            data = s.recv(4096)
            if not data: break
            response.append(data)

        # Close the socket connection
        s.close();

        return ''.join(response)

    def __encode__(self, obj):
        if hasattr(obj, '__json__'):
            return obj.__json__
        return dumps(obj)

    def __decode__(self, json):
        return loads(json)

    def send(self, js):
        return self.__send__(js)

    def json(self, js):
        return self.__decode__(self.__send__(
            "stream.end(JSON.stringify(%s));" % js
        ))

    def wait(self, method, *args):
        if args:
            methodargs = ', '.join(
                [self.__encode__(a) for a in args]
            )
        else:
            methodargs = 'null'

        js = """
        browser.%s(%s, function(err, browser){
            if(err)
                stream.end(JSON.stringify(err.stack));
            else    
                stream.end();
        });
        """ % (
            method,
            methodargs
        )

        return self.__send__(js);

    def kill(self):
        if self.child:
            print "Stopping Zombie.js..."
            self.child.kill()
            self.child = None

        # Cleanup the closed socket
        if os.path.exists(self.socket):
            os.remove(self.socket)
