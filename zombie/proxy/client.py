import socket

try:
    from json import loads, dumps
except ImportError:  # pragma: nocover
    from simplejson import loads, dumps  # noqa

from zombie.compat import PY3

__all__ = ['ZombieProxyClient', 'NodeError']


class NodeError(Exception):
    """
    An exception indicating node.js' failure to parse or evaluate Javascript
    instructions it received.
    """
    pass


class ZombieProxyClient(object):
    """
    Sends data to a ZombieProxyServer bound to a specific
    TCP socket.  Data is evaulated by the server and results
    (if any) are returned.
    """

    def __init__(self, socket):
        """
        Establish a new :class:`ZombieProxyClient`.

        :param socket: a unix socket address to connect to.
        """
        self.socket = socket

    def send(self, js):
        """
        Establishes a socket connection to the Zombie.js server and sends
        Javascript instructions.

        :param js: the Javascript string to execute
        """
        # Establish a socket connection to the Zombie.js proxy server
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.connect(self.socket)

        # Prepend JS to switch to the proper client context.
        js = """
        var _ctx = ctx_switch('%s');
        browser = _ctx[0];
        ELEMENTS = _ctx[1];
        %s
        """ % (id(self), js)

        # Send Zombie.js API calls, followed by a stream.end() call.
        if PY3:  # pragma: nocover
            js = bytes(js, 'utf-8')
        s.send(js)

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

    def json(self, js):
        """
        A shortcut for passing Javascript instructions and decoding a JSON
        response from node.js.

        :param js: the Javascript string to execute
        """
        return self.__decode__(self.send(
            "stream.end(JSON.stringify(%s));" % js
        ))

    def wait(self, method, *args):
        """
        Call a method on the zombie.js Browser instance and wait on a callback.

        :param method: the method to call, e.g., html()
        :param args: one of more arguments for the method
        """
        if args:
            methodargs = ', '.join(
                [self.__encode__(a) for a in args]
            ) + ', '
        else:
            methodargs = ''

        js = """
        try {
            browser.%s(%sfunction(err, browser){
                if (err)
                    stream.end(JSON.stringify(err.stack));
                else
                    stream.end();
            });
        } catch (err) {
            stream.end(JSON.stringify(err.stack));
        }
        """ % (
            method,
            methodargs
        )
        response = self.send(js)
        if response:
            raise NodeError(self.__decode__(response))

    def ping(self):
        """
        Send a simple Javascript instruction and wait on a reply.

        A live Node.JS TCP server will cause this method to return "pong".
        """
        return self.__decode__(
            self.send("stream.end(JSON.stringify(ping));")
        )

    def __encode__(self, obj):
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
