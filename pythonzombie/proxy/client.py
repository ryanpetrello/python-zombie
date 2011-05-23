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
