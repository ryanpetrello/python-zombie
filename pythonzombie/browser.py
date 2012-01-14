from pythonzombie.proxy.server import ZombieProxyServer
from pythonzombie.proxy.client import ZombieProxyClient
import abc


def verb(f):
    """
    Methods that are decorated as `@verb` should always return a reference
    to the original object (e.g., Browser, DOMNode) to allow function chaining.
    """
    def wrap(self, *args, **kwargs):
        f(self, *args, **kwargs)
        return self
    return wrap


class Queryable(object):
    """
    An abstract base class which represents a DOM reference
    point from which a CSS selector can be applied.
    """

    __metaclass__ = abc.ABCMeta

    def _query(self, selector, context=None):
        """
        Evaluate a CSS selector against the document (or an optional context
        DOMNode) and return a list of DOMNode objects.
        """

        #
        # JSON-encode the provided CSS selector so it can be treated as a Javascript
        # query argument.
        #
        # Combine the selector with the (optional) context reference and
        # building a function argstring to be passed to Zombie.js'
        # browser.querySelectorAll() API method.
        #
        args = ','.join(filter(None, [self.encode(selector)]))

        #
        # Run the compiled query, store object (JSDOM Element) references
        # in the TCP server's ELEMENTS cache, and return a stringified list of
        # reference indexes.
        #
        js = """
            var results = [];
            var nodes = %s.querySelectorAll(%s);
            for(var i = 0; i < nodes.length; i++){
                var node = nodes[i];
                ELEMENTS.push(node);
                results.push(ELEMENTS.length - 1);
            };
            stream.end(JSON.stringify(results));
        """ % (
            context if context else 'browser',
            args
        )

        #
        # Translate each index of ELEMENTS into a DOMNode object which can be
        # used to make subsequent object/attribute lookups later.
        #
        return map(
            lambda x: DOMNode(int(x), self.client),
            self.decode(self.client.send(js))
        )

    # Shortcuts for JSON loads/dumps
    def encode(self, value):
        return self.client.encode(value)

    def decode(self, value):
        return self.client.decode(value)


class BaseNode(Queryable):
    """
    More Browser/DOMNode shared functionality.
    """

    def _fill(self, field, value):
        self.client.wait('fill', field, value)


class Browser(BaseNode):
    """
    A Browser object, analogous to zombie.Browser.
    """

    def __init__(self, server=None):
        #
        # If a proxy server isn't specified, spawn one automatically.
        #
        if server is None:
            server = ZombieProxyServer()
        self.client = ZombieProxyClient(server.socket)

    #
    # Document Content
    #
    @property
    def html(self):
        """
        Returns the HTML content of the current document.
        """
        return self.client.json('browser.html()')

    def css(self, selector, context=None):
        """
        Evaluate a CSS selector against the document (or an option context
        DOMNode) and return a list of DOMNode objects.
        """
        return self._query(selector, context)

    #
    # Navigation
    #
    @property
    def location(self):
        return self.client.json('browser.location.toString()')

    @location.setter
    def location(self, url):
        self.visit(url)

    @verb
    def visit(self, url):
        """
        A shortcut to load the document from the specified URL.
        """
        self.client.wait('visit', url)

    #
    # Forms
    #
    @verb
    def fill(self, field, value):
        """
        Fill a specified form field in the current document.
        """
        self._fill(field, value)

    @verb
    def press_button(self, selector):
        """
        Press a specific button (by innerText or CSS selector in the current
        document.
        """
        self.client.wait('pressButton', selector)


class DOMNode(BaseNode):
    """
    Represents a node in the current document's DOM.
    """

    def __init__(self, index, client):
        self.index = index
        self.client = client

    #
    # Inherited functionality
    #
    def css(self, selector):
        """
        Evaluate a CSS selector against this node and return a list of
        (child) DOMNode objects.
        """
        return self._query(selector, self._native)

    @verb
    def fill(self, value):
        """
        If applicable, fill the current node's value.
        """
        self._fill(self, value)

    #
    # Attribute (normal and specialized)
    # access methods.
    #
    @property
    def tagName(self):
        return self._jsonattr('tagName').lower()

    @property
    def value(self):
        if self.tagName == 'textarea':
            return self.textContent
        return self._jsonattr('value')

    @value.setter
    def value(self, value):
        js = """
            var node = %(native)s;
            var tagName = node.tagName;
            if(tagName == "TEXTAREA"){
              node.textContent = %(value)s;
            }else{
                var type = node.getAttribute('type');
                if(type == "checkbox"){
                    %(value)s ? browser.check(node) : browser.uncheck(node);
                }else if(type == "radio"){
                    browser.choose(node);
                }else{
                    browser.fill(node, %(value)s);
                }
            }
            stream.end();
        """ % {
            'native': self._native,
            'value': self.encode(value)
        }
        self.client.send(js)

    @property
    def checked(self):
        return self._jsonattr('checked')

    @checked.setter
    def checked(self, value):
        js = """
            var node = %(native)s;
            var type = node.getAttribute('type');
            if(type == "radio")
                browser.choose(node);
            else
                node.checked = %(value)s;
            stream.end();
        """ % {
            'native': self._native,
            'value': self.encode(value)
        }
        self.client.send(js)

    def _jsonattr(self, attr):
        return self.client.json("%s.%s" % (self._native, attr))

    def __getattr__(self, name):
        return self._jsonattr(name)

    #
    # Events
    #
    @verb
    def fire(self, event):
        self.client.wait('fire', event, self)

    @verb
    def click(self):
        self.fire('click')

    #
    # Private methods
    #
    @property
    def _native(self):
        return "ELEMENTS[%s]" % self.index

    def __repr__(self):
        name, id, className = self.tagName.upper(), self.id, self.className
        if id and className:
            name = "%s#%s.%s" % (name, id, className)
        elif id:
            name = "%s#%s" % (name, id)
        elif className:
            name = "%s.%s" % (name, className)
        return "<%s>" % name

    @property
    def json(self):
        return self._native
