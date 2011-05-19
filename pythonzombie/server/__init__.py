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

    def __init__(self):
        print "Starting Zombie.js..."

        #
        # Spawn the node proxy server in a subprocess.
        # This is a simple socket server that listens for data,
        # evaluates it as Javascript, and passes the eval'ed
        # input to a Zombie.js Browser object.
        #
        args = ['node', self.__proxy_path__()]
        self.process = subprocess.Popen(
            args,
            stdin  = subprocess.PIPE,
            stdout = subprocess.PIPE,
            stderr = subprocess.STDOUT
        )
        self.process.stdin.close()
        time.sleep(.5)

        #
        # Start a thread to monitor and redirect the
        # subprocess stdout and stderr to the console.
        #
        PipeWorker(self.process.stdout).start()

        # When this process ends, clean up the node subprocess
        atexit.register(self.kill)

    def __proxy_path__(self):
        path = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(path, 'server.js')

    def __send__(self, js):
        # Establish a socket connection to the Zombie.js proxy server
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.connect('/tmp/zombie.sock')

        # Send Zombie.js API calls, followed by a stream.end() call.
        self.sock.send("%s" % js)

        # Read the response
        response = []
        while True:
            data = self.sock.recv(4096)
            if not data: break
            response.append(data)

        # Close the socket connection
        self.sock.close();

        return ''.join(response)

    def __encode__(self, obj):
        return dumps(obj)

    def __decode__(self, json):
        return loads(json)

    def attr(self, attr):
        js = """
        stream.end(browser.%s);
        """ % attr
        return self.__send__(js);

    def method(self, method, *args):
        if args:
            argstring = ', '.join(
                [self.__encode__(a) for a in args]
            )
        else:
            argstring = 'null'

        js = """
        stream.end(browser.%s(%s));
        """ % (method, argstring)

        return self.__send__(js);

    def visit(self, *args):
        js = """
        browser.visit(%s, function(err, browser){
            if(err)
                stream.end(JSON.stringify(err.stack));
            else    
                stream.end();
        });
        """ % ', '.join(
            [self.__encode__(a) for a in args]
        )

        return self.__send__(js);

    def kill(self):
        if self.process:
            print "Stopping Zombie.js..."
            self.process.kill()
            self.process = None
