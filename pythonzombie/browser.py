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
    
    def __query__(self, selector, context=None):
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
        args = ','.join(filter(None, [self.__encode__(selector), context]))

        #
        # Run the compiled query, store object (JSDOM Element) references
        # in the TCP server's ELEMENTS cache, and return a stringified list of
        # reference indexes.
        #
        js = """
            var results = [];
            var nodes = browser.querySelectorAll(%s);
            for(var i = 0; i < nodes.length; i++){
                var node = nodes[i];
                ELEMENTS.push(node);
                results.push(ELEMENTS.length - 1);
            };
            stream.end(JSON.stringify(results));
        """ % (
            args
        )

        #
        # Translate each index of ELEMENTS into a DOMNode object which can be
        # used to make subsequent object/attribute lookups later.
        #
        return map(
            lambda x: DOMNode(int(x), self.client),
            self.__decode__(self.client.send(js))
        )

    def __encode__(self, value):
        return self.client.__encode__(value)

    def __decode__(self, value):
        return self.client.__decode__(value)


class BaseNode(Queryable):

    def __fill__(self, field, value):
        js = """
            browser.fill(%s, %s);
            stream.end();
        """ % (
            self.__encode__(field),
            self.__encode__(value)
        )
       
        self.client.send(js)


class Browser(BaseNode):

    def __init__(self, server=None):
        #
        # If a server isn't specified,
        # spawn a new one.
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
        return self.__query__(selector, context)

    #
    # Navigation
    #
    @property
    def location(self):
        return self.client.json('browser.location')

    @location.setter
    def location(self, url):
        self.visit(url)

    @property
    def statusCode(self):
        return self.client.json('browser.statusCode')

    @property
    def redirected(self):
        return self.client.json('browser.redirected')
    
    @verb
    def visit(self, url):
        """
        Load the document from the specified URL.
        """
        self.client.wait('visit', url) 

    #
    # Forms
    #
    @verb
    def fill(self, field, value):
        self.__fill__(field, value)

    @verb
    def pressButton(self, selector):
        self.client.wait('pressButton', selector)


class DOMNode(BaseNode):

    def __init__(self, index, client):
        self.index = index
        self.client = client

    #
    # Inherited functionality
    #
    def css(self, selector):
        """
        Evaluate a CSS selector against this node and return a list of
        child DOMNode objects.
        """
        return self.__query__(selector, self.__native__)

    @verb
    def fill(self, value):
        self.__fill__(self, value)

    #
    # Attribute (normal and specialized)
    # access methods.
    # 
    @property
    def tagName(self):
        return self.__jsonattr__('tagName').lower()
    
    @property
    def value(self):
        if self.tagName == 'textarea':
            return self.textContent
        return self.__jsonattr__('value')

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
            'native'    : self.__native__,
            'value'     : self.__encode__(value)
        }

        self.client.send(js)

    def __jsonattr__(self, attr):
        return self.client.json("%s.%s" % (self.__native__, attr))

    def __getattr__(self, name):
        return self.__jsonattr__(name)

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
    def __native__(self):
        return "ELEMENTS[%s]" % self.index

    def __repr__(self):
        name, id, className = self.tagName, self.id, self.className
        if id:
            name = "%s#%s" % (name, id)
        if className:
            name = "%s.%s" % (name, className)
        return "<%s>" % name

    @property
    def __json__(self):
        return self.__native__
