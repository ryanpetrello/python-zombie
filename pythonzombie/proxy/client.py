from simplejson import loads, dumps
import socket


class ZombieProxyClient(object):
    """
    Sends data to a ZombieProxyServer bound to a specific
    TCP socket.  Data is evaulated by the server and results
    (if any) are returned.
    """

    def __init__(self, socket='/tmp/zombie.sock'):
        self.socket = socket

    def send(self, js):
        # Establish a socket connection to the Zombie.js proxy server
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.connect(self.socket)

        # Send Zombie.js API calls, followed by a stream.end() call.
        s.send("%s" % js)

        # Read the response
        response = []
        while True:
            data = s.recv(4096)
            if not data:
                break
            response.append(data)

        # Close the socket connection
        s.close()

        return ''.join(response)

    def encode(self, obj):
        if hasattr(obj, 'json'):
            return obj.json
        return dumps(obj)

    def decode(self, json):
        return loads(json)

    def json(self, js):
        return self.decode(self.send(
            "stream.end(JSON.stringify(%s));" % js
        ))

    def wait(self, method, *args):
        if args:
            methodargs = ', '.join(
                [self.encode(a) for a in args]
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

        return self.send(js)
