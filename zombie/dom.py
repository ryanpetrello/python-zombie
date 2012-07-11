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

    def _with_context(self, method, selector, context=None):
        """
        Evaluate a CSS selector against the document (or an optional context
        DOMNode) and return decoded text.

        :param method: the method (e.g., html, text) to call on the browser
        :param selector: a string CSS selector
                        (http://zombie.labnotes.org/selectors)
        :param context: an (optional) instance of :class:`DOMNode`
        """

        #
        # JSON-encode the provided CSS selector so it can be treated as
        # a Javascript query argument.
        #
        # Combine the selector with the (optional) context reference and
        # build a function argstring to be passed to Zombie.js'
        # browser.querySelectorAll() API method.
        #
        args = ','.join(filter(None, [self.encode(selector)]))

        if context and hasattr(context, '_native'):
            context = context._native

        #
        # Run the compiled query, store object (JSDOM Element) references
        # in the TCP server's ELEMENTS cache, and return an encoded string.
        #
        js = """
            var results = [];
            var node = browser.%(method)s(%(args)s, %(context)s);
            stream.end(JSON.stringify(node));
        """ % {
            'args': args,
            'context': context if context else 'browser',
            'method': method
        }

        return self.decode(self.client.send(js))

    def _node(self, method, selector, context=None):
        """
        Evaluate a browser method and CSS selector against the document
        (or an optional context DOMNode) and return a single DOMNode object,
        e.g.,

        browser._node('query', 'body > div')

        ...roughly translates to the following Javascript...

        browser.query('body > div')

        :param method: the method (e.g., query) to call on the browser
        :param selector: a string CSS selector
                        (http://zombie.labnotes.org/selectors)
        :param context: an (optional) instance of :class:`DOMNode`
        """

        #
        # JSON-encode the provided CSS selector so it can be treated as
        # a Javascript query argument.
        #
        # Combine the selector with the (optional) context reference and
        # build a function argstring to be passed to Zombie.js'
        # browser.querySelectorAll() API method.
        #
        args = ','.join(filter(None, [self.encode(selector)]))

        #
        # Run the compiled query, store object (JSDOM Element) references
        # in the TCP server's ELEMENTS cache, and return a stringified list of
        # reference indexes.
        #
        js = """
            var node = browser.%(method)s(%(args)s, %(context)s);
            if(node){
                ELEMENTS.push(node);
                stream.end(JSON.stringify(ELEMENTS.length - 1));
            }
            stream.end();
        """

        js = js % {
            'method': method,
            'args': args,
            'context': context if context else 'browser'
        }

        #
        # If a reference is returned, translate the reference into a DOMNode
        # object which can be used to make subsequent object/attribute lookups
        # later.
        #
        decoded = self.decode(self.client.send(js))
        if decoded is not None:
            return DOMNode(decoded, self.client)

    def _nodes(self, method, selector, context=None):
        """
        Similar to ``_node``, but returns every match (rather than just one).

        :param method: the method (e.g., query) to call on the browser
        :param selector: a string CSS selector
                        (http://zombie.labnotes.org/selectors)
        :param context: an (optional) instance of :class:`DOMNode`
        """

        #
        # JSON-encode the provided CSS selector so it can be treated as
        # a Javascript query argument.
        #
        # Combine the selector with the (optional) context reference and
        # build a function argstring to be passed to Zombie.js'
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
            var nodes = browser.%(method)s(%(args)s, %(context)s);
            for(var i = 0; i < nodes.length; i++){
                var node = nodes[i];
                ELEMENTS.push(node);
                results.push(ELEMENTS.length - 1);
            };
            stream.end(JSON.stringify(results));
        """

        js = js % {
            'method': method,
            'args': args,
            'context': context if context else 'browser'
        }

        #
        # Translate each index of ELEMENTS into a DOMNode object which can be
        # used to make subsequent object/attribute lookups later.
        #
        return [
            DOMNode(int(x), self.client)
            for x in self.decode(self.client.send(js))
        ]

    # Shortcuts for JSON loads/dumps
    def encode(self, value):
        return self.client.__encode__(value)

    def decode(self, value):
        return self.client.__decode__(value)


class BaseNode(Queryable):
    """
    More Browser/DOMNode shared functionality.
    """

    def _fill(self, field, value):
        self.client.wait('fill', field, value)


class DOMNode(BaseNode):
    """
    :class:`.DOMNode` represents a node in the current document's DOM.
    """

    def __init__(self, index, client):
        self.index = index
        self.client = client

    #
    # Inherited functionality
    #
    def query(self, selector):
        """
        Evaluate a CSS selector against this node and return a single

        (child) DOMNode object.
        """
        return self._node('query', selector, self._native)

    def queryAll(self, selector):
        """
        Evaluate a CSS selector against this node and return a list of
        (child) DOMNode objects.
        """
        return self._nodes('queryAll', selector, self._native)

    def css(self, selector):
        """
        An alias for DOMNode.queryAll.
        """
        return self.queryAll(selector)

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

    def __getitem__(self, name):
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
