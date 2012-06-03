import socket

try:
    from json import loads, dumps
except ImportError:  # pragma: nocover
    from simplejson import loads, dumps  # noqa

from pythonzombie.compat import PY3


class NodeError(Exception):
    pass


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
        out = "%s" % js
        if PY3:  # pragma: nocover
            out = bytes(out, 'utf-8')
        s.send(out)

        # Read the response
        response = []
        while True:
            data = s.recv(4096)
            if not data:
                break
            if PY3:  # pragma: nocover
                data = str(data, 'utf-8')
            response.append(data)

        # Close the socket connection
        s.close()

        return ''.join(response)

    def encode(self, obj):
        if hasattr(obj, 'json'):
            return obj.json
        if hasattr(obj, '__json__'):
            return obj.__json__()
        return dumps(obj)

    def __decode__(self, json):
        if json:
            return loads(json)
        else:
            return None

    def json(self, js):
        return self.__decode__(self.__send__(
            "stream.end(JSON.stringify(%s));" % js
        ))

    def wait(self, method, *args):
        if args:
            methodargs = ', '.join(
                [self.encode(a) for a in args]
            ) + ', '
        else:
            methodargs = 'null,'

        js = """
        try {
            browser.%s(%s function(err, browser){
                if (err)
                    stream.end(JSON.stringify(err.message));
                else
                    stream.end();
            });
        } catch (err) {
            stream.end(JSON.stringify(err.message));
        }
        """ % (
            method,
            methodargs
        )
        response = self.__send__(js)
        if response:
            raise NodeError(self.__decode__(response))

    def ping(self):
        return self.__decode__(
            self.__send__("stream.end(JSON.stringify(ping));")
        )
