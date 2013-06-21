import socket

try:
    from json import loads, dumps
except ImportError:  # pragma: nocover
    from simplejson import loads, dumps  # noqa

from zombie.compat import PY3

__all__ = ['ZombieProxyClient', 'NodeError']


def _encode(obj):
    if hasattr(obj, 'json'):
        return obj.json
    if hasattr(obj, '__json__'):
        return obj.__json__()
    return dumps(obj)


def _decode(json):
    if json:
        return loads(json)
    else:
        return None


class NodeError(Exception):
    """
    An exception indicating node.js' failure to parse or evaluate Javascript
    instructions it received.
    """
    pass


class ZombieProxyClient(object):
    """
    Sends data to a :class:`zombie.proxy.server.ZombieProxyServer` bound to
    a specific TCP socket.  Data is evaulated by the server and results
    (if any) are returned.
    """
    __encode__ = staticmethod(_encode)
    __decode__ = staticmethod(_decode)

    def __init__(self, socket):
        """
        Establish a new :class:`ZombieProxyClient`.

        :param socket: a unix socket address to connect to.
        """
        self.socket = socket

    def send(self, js):
        """
        Establishes a socket connection to the zombie.js server and sends
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

    def nowait(self, method, *args):
        """
        There are methods that do not support callback
        """
        methodargs = encode_args(args)
        js = """
        try {
            browser.%s(%s);
            stream.end();
        } catch (err) {
            stream.end(JSON.stringify(err.stack));
        }
        """ % (method, methodargs)
        response = self.send(js)
        if response:
            raise NodeError(self.__decode__(response))

    def wait(self, method, *args):
        """
        Call a method on the zombie.js Browser instance and wait on a callback.

        :param method: the method to call, e.g., html()
        :param args: one of more arguments for the method
        """
        methodargs = encode_args(args, extra=True)
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
        """ % (method, methodargs)
        response = self.send(js)
        if response:
            raise NodeError(self.__decode__(response))

    def ping(self):
        """
        Send a simple Javascript instruction and wait on a reply.

        A live node.js TCP server will cause this method to return "pong".
        """
        return self.__decode__(
            self.send("stream.end(JSON.stringify(ping));")
        )


def encode_args(args, extra=False):
    """Encode args for js execution"""
    if args:
        methodargs = ', '.join(
            [_encode(a) for a in args]
        )
        if extra:
            methodargs += ', '
    else:
        methodargs = ''
    return methodargs
