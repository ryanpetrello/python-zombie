import contextlib
import socket

try:
    from json import loads, dumps
except ImportError:  # pragma: nocover
    from simplejson import loads, dumps  # noqa

from zombie.compat import PY3

__all__ = ['ZombieProxyClient', 'NodeError']


def encode(obj):
    """
    Encode one argument/object to json
    """
    if hasattr(obj, 'json'):
        return obj.json
    if hasattr(obj, '__json__'):
        return obj.__json__()
    return dumps(obj)


def encode_args(args, extra=False):
    """
    Encode a list of arguments
    """
    if not args:
        return ''

    methodargs = ', '.join([encode(a) for a in args])
    if extra:
        methodargs += ', '

    return methodargs


def decode(json):
    """
    Decode json.

    Returns None if None is given as json
    """
    if json is None:
        return None
    return loads(json)


class Element(object):
    """
    Reference to an element stored in the nodejs server
    """
    def __init__(self, index):
        self.__index = index

    @property
    def index(self):
        return self.__index

    @property
    def json(self):
        return "ELEMENTS[%s]" % self.__index

    def __str__(self):
        return self.json


class NodeError(Exception):
    """
    An exception indicating node.js' failure to parse or evaluate Javascript
    instructions it received.
    """
    pass


class ZombieServerConnection(object):
    def __init__(self, socket_address):
        self.__socket_address = socket_address

    def send(self, data):
        if PY3:  # pragma: nocover
            data = bytes(data, 'utf-8')

        with self._open_connection() as con:
            con.send(data)
            response = self._receive(con)

        return response

    def _open_connection(self):
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.connect(self.__socket_address)
        return contextlib.closing(sock)

    def _receive(self, con):
        response = []
        while True:
            data = con.recv(4096)
            if not data:
                break
            if PY3:  # pragma: nocover
                data = str(data, 'utf-8')
            response.append(data)
        return ''.join(response)


class ZombieProxyClient(object):
    """
    Sends data to a :class:`zombie.proxy.server.ZombieProxyServer` bound to
    a specific TCP socket.  Data is evaulated by the server and results
    (if any) are returned.
    """

    def __init__(self, socket_address):
        """
        Establish a new :class:`ZombieProxyClient`.

        :param socket: a unix socket address to connect to.
        """
        self.connection = ZombieServerConnection(socket_address)

    def _send(self, javascript):
        """
        Establishes a socket connection to the zombie.js server and sends
        Javascript instructions.

        :param js: the Javascript string to execute
        """

        # Prepend JS to switch to the proper client context.
        message = """
            var _ctx = ctx_switch('%s'),
                browser = _ctx[0],
                ELEMENTS = _ctx[1];
            %s
        """ % (id(self), javascript)

        response = self.connection.send(message)

        return self._handle_response(response)

    def _handle_response(self, response):
        errno, result = decode(response)
        if errno == 1:
            raise NodeError(result)
        return result

    def json(self, js, args=None):
        """
        A shortcut for passing Javascript instructions and decoding a JSON
        response from node.js.

        :param js: the Javascript string to execute
        """
        return self.nowait("result = %s" % js, args)

    def nowait(self, js, args=None):
        if args:
            js = "%s(%s)" % (js, encode_args(args))

        js = """
            %s;
            return_result(result);
        """ % js
        return self._send(js)

    def wait(self, method, *args):
        """
        Call a method on the zombie.js Browser instance and wait on a callback.

        :param method: the method to call, e.g., html()
        :param args: one of more arguments for the method
        """
        methodargs = encode_args(args, extra=True)
        js = """
        %s(%s wait_callback);
        """ % (method, methodargs)
        self._send(js)

    def wait_return(self, method, *args):
        """
        Call a method on the zombie.js Browser instance and wait on a callback.

        :param method: the method to call, e.g., html()
        :param args: one of more arguments for the method
        """
        methodargs = encode_args(args, extra=True)
        js = """
        %s(%s wait_n_return_callback);
        """ % (method, methodargs)
        return self._send(js)

    def ping(self):
        """
        Send a simple Javascript instruction and wait on a reply.

        A live node.js TCP server will cause this method to return "pong".
        """
        return self.json('ping')

    def cleanup(self):
        """
        Destroy and clean up any browser and elements in the server

        As new browsers are created, memory will be reserved in the node
        process. In order to avoid memory problems you will need to clean up
        those browsers or one by one, or using this clean up in a specific
        moment in your code
        """
        self.nowait('cleanup()')

    def create_element(self, method, args=None):
        """
        Evaluate a browser method and CSS selector against the document
        (or an optional context DOMNode) and return a single
        :class:`zombie.dom.DOMNode` object, e.g.,

        browser._node('query', 'body > div')

        ...roughly translates to the following Javascript...

        browser.query('body > div')

        :param method: the method (e.g., query) to call on the browser
        :param selector: a string CSS selector
                        (http://zombie.labnotes.org/selectors)
        :param context: an (optional) instance of :class:`zombie.dom.DOMNode`
        """
        if args is None:
            arguments = ''
        else:
            arguments = "(%s)" % encode_args(args)
        js = """
            create_element(ELEMENTS, %(method)s%(args)s);
        """ % {
            'method': method,
            'args': arguments
        }

        index = self.json(js)
        if index is None:
            return None

        return Element(index)

    def create_elements(self, method, args=[]):
        """
        Execute a browser method that will return a list of elements.

        Returns a list of the element indexes
        """
        args = encode_args(args)

        js = """
            create_elements(ELEMENTS, %(method)s(%(args)s))
        """ % {
            'method': method,
            'args': args,
        }

        indexes = self.json(js)
        return map(Element, indexes)
