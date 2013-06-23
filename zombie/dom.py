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
        :param context: an (optional) instance of :class:`zombie.dom.DOMNode`
        """

        #
        # JSON-encode the provided CSS selector so it can be treated as
        # a Javascript query argument.
        #
        # Combine the selector with the (optional) context reference and
        # build a function argstring to be passed to Zombie.js.
        #
        args = ','.join(filter(None, [self.encode(selector)]))

        if context and hasattr(context, '_native'):
            context = context._native

        #
        # Run the method (with compiled args) and return an encoded string.
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

        #
        # JSON-encode the provided CSS selector so it can be treated as
        # a Javascript query argument.
        #
        # Combine the selector with the (optional) context reference and
        # build a function argstring to be passed to Zombie.js.
        #
        args = ','.join(filter(None, [self.encode(selector)]))

        #
        # Run the compiled query, store an object (JSDOM Element) reference
        # in the TCP server's ELEMENTS cache, and return a stringified
        # reference index.
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
        # build a function argstring to be passed to Zombie.js.
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
    #
    # Forms
    #
    def fill(self, field, value):
        """
        Fill a specified form field in the current document.

        :param field: an instance of :class:`zombie.dom.DOMNode`
        :param value: any string value
        :return: self to allow function chaining.
        """
        self.client.nowait('fill', field, value)
        return self

    def pressButton(self, selector):
        """
        Press a specific button.

        :param selector: CSS selector or innerText
        :return: self to allow function chaining.
        """
        self.client.wait('pressButton', selector)
        return self

    def check(self, selector):
        self.client.nowait('check', selector)
        return self

    def select(self, selector, value):
        self.client.nowait('select', selector, value)
        return self

    def selectOption(self, selector):
        self.client.nowait('selectOption', selector)
        return self

    def unselect(self, selector, value):
        self.client.nowait('unselect', selector, value)
        return self

    def unselectOption(self, selector):
        self.client.nowait('unselectOption', selector)
        return self

    def attach(self, selector, filename):
        self.client.nowait('attach', selector, filename)
        return self

    #
    # query
    #
    def field(self, selector, context=None):
        return self._node('field', selector, context)


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
    def query(self, selector):
        """
        Evaluate a CSS selector against this element and return a single
        (child) :class:`zombie.dom.DOMNode` object.

        :param selector: a string CSS selector
                        (http://zombie.labnotes.org/selectors)
        """
        return self._node('query', selector, self._native)

    def queryAll(self, selector):
        """
        Evaluate a CSS selector against this element and return a list of
        (child) :class:`zombie.dom.DOMNode` objects.

        :param selector: a string CSS selector
                        (http://zombie.labnotes.org/selectors)
        """
        return self._nodes('queryAll', selector, self._native)

    def css(self, selector):
        """
        An alias for :class:`zombie.dom.DOMNode.queryAll`.
        """
        return self.queryAll(selector)

    #
    # Forms
    #
    def fill(self, value):
        """
        If applicable, fill the current node's value.

        :param value: any string value

        Returns the :class:`zombie.dom.DOMNode` to allow function chaining.
        """
        return super(DOMNode, self).fill(self, value)

    def pressButton(self):
        """
        If applicable, press this button

        Returns the :class:`zombie.dom.DOMNode` to allow function chaining.
        """
        return super(DOMNode, self).pressButton(self)

    def check(self):
        """
        If applicable, Checks a checkbox

        Returns the :class:`zombie.dom.DOMNode` to allow function chaining.
        """
        return super(DOMNode, self).check(self)

    def uncheck(self):
        """
        If applicable, unchecks a checkbox

        Returns the :class:`zombie.dom.DOMNode` to allow function chaining.
        """
        return super(DOMNode, self).uncheck(self)

    def select(self, value):
        """
        If applicable, selects an option

        :param value: Value (or label) or option to select

        Returns the :class:`zombie.dom.DOMNode` to allow function chaining.
        """
        return super(DOMNode, self).select(self, value)

    def selectOption(self):
        """
        If applicable, selects this option

        Returns the :class:`zombie.dom.DOMNode` to allow function chaining.
        """
        return super(DOMNode, self).selectOption(self)

    def unselect(self, value):
        """
        If applicable, unselect an option

        :param value: Value (or label) or option to unselect

        Returns the :class:`zombie.dom.DOMNode` to allow function chaining.
        """
        return super(DOMNode, self).unselect(self, value)

    def unselectOption(self):
        """
        If applicable unselect this option

        Returns the :class:`zombie.dom.DOMNode` to allow function chaining.
        """
        return super(DOMNode, self).unselectOption(self)

    def attach(self, filename):
        """
        If applicable, attaches a file to the specified input field

        :param filename: Filename of the file to attach.

        Returns the :class:`zombie.dom.DOMNode` to allow function chaining.
        """
        return super(DOMNode, self).attach(self, filename)

    def field(self):
        """
        The field of a :class:`zombie.dom.DOMNode` is itself. Returns self.
        """
        return self

    #
    # Attribute (normal and specialized)
    # access methods.
    #
    @property
    def text(self):
        """
        The ``textContent`` of the current node.
        """
        return self.textContent

    @property
    def innerText(self):
        """
        The ``textContent`` of the current node.
        """
        return self.textContent

    @property
    def html(self):
        """
        The ``innerHTML`` of the current node.
        """
        return self.innerHTML

    @property
    def tagName(self):
        """
        The ``tagName`` of the current node.
        """
        return self._jsonattr('tagName').lower()

    @property
    def value(self):
        """
        The ``value`` of the current node.
        """
        if self.tagName == 'textarea':
            return self.textContent
        return self._jsonattr('value')

    @value.setter
    def value(self, value):
        """
        Used to set the ``value`` of form elements.
        """
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
        """
        The ``checked`` attribute of an ``<input type="checkbox">``.
        """
        return self._jsonattr('checked')

    @checked.setter
    def checked(self, value):
        """
        Used to set the ``checked`` attribute of an ``<input
        type="checkbox">``.
        """
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
    def fire(self, event):
        """
        Fires a specified DOM event on the current node.

        :param event: the name of the event to fire (e.g., 'click').

        Returns the :class:`zombie.dom.DOMNode` to allow function chaining.
        """
        self.client.wait('fire', self, event)
        return self

    def click(self):
        """
        Fires a ``click`` event on the current node.

        Returns the :class:`zombie.dom.DOMNode` to allow function chaining.
        """
        self.fire('click')
        return self

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
        """
        The JSON representation of the current node.
        """
        return self._native
