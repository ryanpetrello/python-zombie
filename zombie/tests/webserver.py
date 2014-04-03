import logging
import os.path
import random
import threading
from wsgiref.simple_server import make_server, WSGIRequestHandler
from zombie.compat import TestCase, to_bytes

logger = logging.getLogger(__name__)


class WSGIRunner(threading.Thread):
    """
    Wraps a WSGI application in a thread
    """
    def __init__(self, app):
        """Creates the runner with a server inside"""
        super(WSGIRunner, self).__init__()
        self.server = make_server(
            '', 0, app, handler_class=TestWSGIRequestHandler)
        self.daemon = True

    @property
    def port(self):
        """Port assigned to the HTTP server"""
        return self.server.server_address[1]

    def run(self):
        """Used by :class:`threading.Thread` to start the thread"""
        self.server.serve_forever()

    def stop(self):
        """Shutdown the WSGI server and wait for the thread to finish"""
        self.server.shutdown()
        self.join()


class TestWSGIRequestHandler(WSGIRequestHandler):
    """
    This request handler overrides some default functionality:
    - Logging of messages
    """
    # Enable keepalive (default is HTTP/1.0)
    protocol_version = "HTTP/1.1"

    def address_string(self):
        """Client address 'host:port' formatted"""
        host, port = self.client_address[:2]
        return '%s:%s' % (host, port)

    def _log(self, level, msg):
        """Log to the module logger"""
        logger.log(level, msg)

    def log_message(self, format, *args):
        """Override the stdout logging"""
        msg = "%s - - [%s] %s" % (
            self.address_string(),
            self.log_date_time_string(), format % args)
        self._log(logging.INFO, msg)


class AppBuilder(object):
    def __init__(self, base_path):
        self.base = base_path
        self.routes = {}

    def add_html(self, method, path, filename):
        filepath = os.path.join(self.base, filename)
        with open(filepath, 'r') as html_file:
            contents = to_bytes(html_file.read())

        def action(environ, start_response):
            start_response(
                '200 OK',
                [('Content-Type', 'text/html')])
            return contents

        self.add_route(method, path, action)

    def add_redirect(self, method, path, redirect_to):
        def action(environ, start_response):
            response_headers = [
                ('Location', redirect_to),
                ('Content-type', 'text/plain')
            ]
            start_response('302 Found', response_headers)
            return to_bytes('')
        self.add_route(method, path, action)

    def add_route(self, method, path, action):
        route_item = self.routes.get(path, {})
        route_item[method] = action
        self.routes[path] = route_item

    def __call__(self, environ, start_response):
        return App(self.routes, environ, start_response)


class App(object):
    def __init__(self, routes, environ, start_response):
        self.routes = routes
        self.environ = environ
        self.start_response = start_response

    @property
    def path_info(self):
        """The environ['PATH_INFO']"""
        return self.environ['PATH_INFO']

    @property
    def request_method(self):
        """The environ['REQUEST_METHOD']"""
        return self.environ['REQUEST_METHOD']

    def __iter__(self):
        """
        A sample WSGI app that forcibly redirects all requests to /
        """
        route = self.routes.get(self.path_info, {})
        action = route.get(self.request_method, None)
        if action is None:
            yield self.not_found()
        else:
            yield action(self.environ, self.start_response)

    def not_found(self):
        """Called if no URL matches."""
        self.start_response(
            '404 NOT FOUND',
            [('Content-Type', 'text/plain')])
        return to_bytes('Not Found')


def build_test_app():
    """Configure the test app"""
    module_path = os.path.dirname(os.path.abspath(__file__))
    base = os.path.join(module_path, 'helpers')

    builder = AppBuilder(base)
    builder.add_html('GET', '/', 'index.html')
    builder.add_html('GET', '/location2', 'location2.html')
    builder.add_html('POST', '/submit', 'submit.html')
    builder.add_redirect('GET', '/redirect', '/')
    return builder


class WebServerTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        """Starts the HTTP server with some basic urls"""
        app = build_test_app()
        cls.runner = WSGIRunner(app)
        cls.runner.start()

    @classmethod
    def tearDownClass(cls):
        """Stop the server"""
        cls.runner.stop()
        cls.runner = None

    @property
    def base_url(self):
        """URL with port about where is the server serving"""
        return 'http://127.0.0.1:%s/' % self.runner.port
