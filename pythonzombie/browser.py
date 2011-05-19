from pythonzombie.server import ZombieProxyServer
import abc

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
            lambda x: DOMNode(int(x), self.server),
            self.__decode__(self.server.send(js))
        )

    def __encode__(self, value):
        return self.server.__encode__(value)

    def __decode__(self, value):
        return self.server.__decode__(value)


class BaseNode(Queryable):

    def __fill__(self, field, value):
        js = """
            browser.fill(%s, %s);
            stream.end();
        """ % (
            self.__encode__(field),
            self.__encode__(value)
        )
       
        self.server.send(js)
        return self


class Browser(BaseNode):

    def __init__(self, server=None):
        if server:
            self.server = server
        else:
            self.server = ZombieProxyServer()

    #
    # Document Content
    #
    @property
    def html(self):
        """
        Returns the HTML content of the current document.
        """
        return self.server.json('browser.html()')

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
        return self.server.json('browser.location')

    @location.setter
    def location(self, url):
        self.visit(url)

    @property
    def statusCode(self):
        return self.server.json('browser.statusCode')

    @property
    def redirected(self):
        return self.server.json('browser.redirected')
    
    def visit(self, url):
        """
        Load the document from the specified URL.
        """
        self.server.wait('visit', url) 

    #
    # Forms
    #
    def fill(self, field, value):
        return self.__fill__(field, value)

    def pressButton(self, selector):
        self.server.wait('pressButton', selector)


class DOMNode(BaseNode):

    def __init__(self, index, server):
        self.index = index
        self.server = server

    #
    # Inherited functionality
    #
    def css(self, selector):
        """
        Evaluate a CSS selector against this node and return a list of
        child DOMNode objects.
        """
        return self.__query__(selector, self.__native__)

    def fill(self, value):
        return self.__fill__(self, value)

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

        self.server.send(js)

    def __jsonattr__(self, attr):
        return self.server.json("%s.%s" % (self.__native__, attr))

    def __getattr__(self, name):
        return self.__jsonattr__(name)

    #
    # Events
    #
    def click(self):
        self.server.wait('fire', 'click', self)

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
