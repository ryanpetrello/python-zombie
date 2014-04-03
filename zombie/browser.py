from zombie.proxy.server import ZombieProxyServer
from zombie.proxy.client import ZombieProxyClient

__all__ = ['Browser', 'DOMNode']


class Literal(object):
    def __init__(self, value):
        self.__value = value

    @property
    def json(self):
        return self.__value


class Browser(object):
    """
    A Browser object, analogous to zombie.js' ``Browser``.
    """

    def __init__(self, server=None):
        """
        Start a new Browser instance.

        :param server: an (optional) instance of
                       :class:`zombie.proxy.server.ZombieProxyServer`.
        """
        #
        # If a proxy server isn't specified, spawn one automatically.
        #
        if server is None:
            server = ZombieProxyServer()
        self.server = server
        self.client = ZombieProxyClient(server.socket)

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
        self.client.nowait('browser.fill', (field, value))
        return self

    def pressButton(self, selector):
        """
        Press a specific button.

        :param selector: CSS selector or innerText
        :return: self to allow function chaining.
        """
        self.client.wait('browser.pressButton', selector)
        return self

    def check(self, selector):
        self.client.nowait('browser.check', (selector,))
        return self

    def uncheck(self, selector):
        self.client.nowait('browser.uncheck', (selector,))
        return self

    def select(self, selector, value):
        self.client.nowait('browser.select', (selector, value))
        return self

    def selectOption(self, selector):
        self.client.nowait('browser.selectOption', (selector,))
        return self

    def unselect(self, selector, value):
        self.client.nowait('browser.unselect', (selector, value))
        return self

    def attach(self, selector, filename):
        self.client.nowait('browser.attach', (selector, filename))
        return self

    def choose(self, selector):
        self.client.nowait('browser.choose', (selector, ))
        return self

    #
    # query
    #
    def field(self, selector, context=None):
        element = self.client.create_element(
            'browser.field', (selector, context))
        return DOMNode(element, self)

    #
    # Document Content
    #
    def load(self, html):
        """
        Loads raw html
        """
        self.client.wait('browser.load', html)

    @property
    def body(self):
        """
        Returns a :class:`zombie.dom.DOMNode` representing the body element of
        the current document.
        """
        element = self.client.create_element('browser.body')
        return DOMNode(element, self)

    def html(self, selector=None, context=None):
        """
        Returns the HTML content (string) of the current document.

        :param selector: an optional string CSS selector
                        (http://zombie.labnotes.org/selectors)
        :param context: an (optional) instance of :class:`zombie.dom.DOMNode`
        """
        return self.client.json('browser.html', (selector, context))

    def query(self, selector, context=None):
        """
        Evaluate a CSS selector against the document (or an optional context
        :class:`zombie.dom.DOMNode`) and return a single
        :class:`zombie.dom.DOMNode` object.

        :param selector: a string CSS selector
                        (http://zombie.labnotes.org/selectors)
        :param context: an (optional) instance of :class:`zombie.dom.DOMNode`
        """
        element = self.client.create_element(
            'browser.query', (selector, context))
        return DOMNode.factory(element, self)

    def queryAll(self, selector, context=None):
        """
        Evaluate a CSS selector against the document (or an optional context
        :class:`zombie.dom.DOMNode`) and return a list of
        :class:`zombie.dom.DOMNode` objects.

        :param selector: a string CSS selector
                        (http://zombie.labnotes.org/selectors)
        :param context: an (optional) instance of :class:`zombie.dom.DOMNode`
        """
        elements = self.client.create_elements(
            'browser.queryAll', (selector, context))
        return [DOMNode(e, self) for e in elements]

    def css(self, selector, context=None):
        """
        An alias for :class:`zombie.browser.Browser.queryAll`.

        :param selector: a string CSS selector
                        (http://zombie.labnotes.org/selectors)
        :param context: an (optional) instance of :class:`zombie.dom.DOMNode`
        """
        return self.queryAll(selector, context)

    def text(self, selector, context=None):
        """
        Returns the text content of specific elements.

        :param selector: a string CSS selector
                        (http://zombie.labnotes.org/selectors)
        :param context: an (optional) instance of :class:`zombie.dom.DOMNode`
        """
        return self.client.json('browser.text', (selector, context))

    def unselectOption(self, selector):
        """
        Unselects the given option

        Special case. It seems there is a problem in Zombie: unselectOption
        doesn't accept a selector.

        Pull request pending in the zombie project
        """
        self.query(selector).unselectOption()
        return self

    #
    # Navigation
    #
    def clickLink(self, selector):
        """
        Clicks on a link. The first argument is the link text or CSS selector.

        :param selector: an optional string CSS selector
                        (http://zombie.labnotes.org/selectors) or inner text

        Returns the :class:`zombie.browser.Browser` to allow function chaining.
        """
        self.client.wait('browser.clickLink', selector)
        return self

    @property
    def location(self):
        """
        Returns the location of the current document (same as
        ``window.location.toString()``).
        """
        return self.client.json('browser.location.toString()')

    @location.setter
    def location(self, url):
        """
        Changes document location, loading a new document if necessary (same as
        setting ``window.location``). This will also work if you just need to
        change the hash (Zombie.js will fire a hashchange event).
        """
        self.visit(url)

    def visit(self, url):
        """
        A shortcut to load the document from the specified URL.

        Returns the :class:`zombie.browser.Browser` to allow function chaining.
        """
        self.client.wait('browser.visit', url)
        return self

    def back(self):
        """
        Navigate to the previous page in history.

        Returns the :class:`zombie.browser.Browser` to allow function chaining.
        """
        self.client.wait('browser.back')
        return self

    def link(self, selector):
        """
        Finds and returns a link ``<a>`` element (:class:`zombie.dom.DOMNode`).
        You can use a CSS selector or find a link by its text contents (case
        sensitive, but ignores leading/trailing spaces).

        :param selector: an optional string CSS selector
                        (http://zombie.labnotes.org/selectors) or inner text
        """
        element = self.client.create_element('browser.link', (selector,))
        return DOMNode(element, self)

    def reload(self):
        """
        Reloads the current page.

        Returns the :class:`zombie.browser.Browser` to allow function chaining.
        """
        self.client.wait('browser.reload')
        return self

    @property
    def statusCode(self):
        """
        Returns the status code returned for this page request (200, 303, etc).
        """
        return self.client.json('browser.statusCode')

    @property
    def success(self):
        """
        Returns ``True`` if the status code is 2xx.
        """
        return self.client.json('browser.success')

    @property
    def redirected(self):
        """
        Returns ``True`` if the page request followed a redirect.
        """
        return self.client.json('browser.redirected')

    def fire(self, selector, event_name):
        self.client.wait('browser.fire', selector, event_name)
        return self

    #
    # Debugging
    #
    def dump(self):
        """
        Prints a debug string including zombie.js version, current URL,
        history, cookies, event loop, etc.  Useful for debugging and submitting
        error reports.
        """
        self.client.json('browser.dump()')

    def get_resource(self, url):
        """
        Gets a resource and returns a json with information
        """
        return self.client.wait_return('browser.resources.get', url)

    def post_resource(self, url, form_params):
        options = {
            'headers': {
                'content-type': 'application/x-www-form-urlencoded'},
            'params': form_params}
        return self.client.wait_return('browser.resources.post', url, options)

    def evaluate(self, code):
        return self.client.json('browser.evaluate', (code, ))

    def wait(self, wait_argument=None):
        arguments = [] if wait_argument is None else [wait_argument]
        self.client.wait('browser.wait', *arguments)

    @property
    def resources(self):
        """
        Returns a list of resources loaded by the browser, e.g.,
        ::
            [{
                'method': 'GET',
                'url': 'http://www.example.com/',
                'statusCode': '200',
                'statusText': 'OK',
                'time': '200ms'
            }]
        """
        js = """
            browser.resources.map(
                function(r){
                    var request = r.request;
                    var response = r.response;
                    return {
                        'method': request.method,
                        'url': request.url,
                        'statusCode': response.statusCode,
                        'statusText': response.statusText,
                        'time': (response.time - request.time) + 'ms',
                    }
                }
            )
        """
        return self.client.json(js)

    def viewInBrowser(self):
        """
        Views the current document in a real Web browser. Uses the default
        system browser on OS X, BSD and Linux. Probably errors on Windows.
        """
        return self.client.send('browser.viewInBrowser()')  # pragma: nocover


class DOMNode(object):
    """
    Represents a node in the current document's DOM.
    """
    @staticmethod
    def factory(element, browser):
        if element is None:
            return None
        return DOMNode(element, browser)

    def __init__(self, element, browser):
        self.element = element
        self.client = browser.client
        self.browser = browser

    def query(self, selector):
        """
        Evaluate a CSS selector against this element and return a single
        (child) :class:`zombie.dom.DOMNode` object.

        :param selector: a string CSS selector
                        (http://zombie.labnotes.org/selectors)
        """
        return self.browser.query(selector, self.element)

    def queryAll(self, selector):
        """
        Evaluate a CSS selector against this element and return a list of
        (child) :class:`zombie.dom.DOMNode` objects.

        :param selector: a string CSS selector
                        (http://zombie.labnotes.org/selectors)
        """
        return self.browser.queryAll(selector, self.element)

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
        return self.browser.fill(self.element, value)

    def pressButton(self):
        """
        If applicable, press this button

        Returns the :class:`zombie.dom.DOMNode` to allow function chaining.
        """
        return self.browser.pressButton(self.element)

    def check(self):
        """
        If applicable, Checks a checkbox

        Returns the :class:`zombie.dom.DOMNode` to allow function chaining.
        """
        return self.browser.check(self.element)

    def uncheck(self):
        """
        If applicable, unchecks a checkbox

        Returns the :class:`zombie.dom.DOMNode` to allow function chaining.
        """
        return self.browser.uncheck(self.element)

    def select(self, value):
        """
        If applicable, selects an option

        :param value: Value (or label) or option to select

        Returns the :class:`zombie.dom.DOMNode` to allow function chaining.
        """
        return self.browser.select(self.element, value)

    def selectOption(self):
        """
        If applicable, selects this option

        Returns the :class:`zombie.dom.DOMNode` to allow function chaining.
        """
        return self.browser.selectOption(self.element)

    def unselect(self, value):
        """
        If applicable, unselect an option

        :param value: Value (or label) or option to unselect

        Returns the :class:`zombie.dom.DOMNode` to allow function chaining.
        """
        return self.browser.unselect(self.element, value)

    def unselectOption(self):
        """
        If applicable unselect this option

        Returns the :class:`zombie.dom.DOMNode` to allow function chaining.
        """
        return self.client.nowait('browser.unselectOption', (self.element,))

    def attach(self, filename):
        """
        If applicable, attaches a file to the specified input field

        :param filename: Filename of the file to attach.

        Returns the :class:`zombie.dom.DOMNode` to allow function chaining.
        """
        return self.browser.attach(self.element, filename)

    def choose(self):
        """
        If applicable, chooses this radio button
        """
        return self.browser.choose(self.element)

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
        self.client.nowait(
            'set_field', (Literal('browser'), self.element, value))

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
        self.client.nowait(
            'check_field', (Literal('browser'), self.element, value))

    def _jsonattr(self, attr):
        return self.client.json("%s.%s" % (self.element.json, attr))

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
        self.browser.fire(self.element, event)
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
    def json(self):
        return self.element.json

    def __repr__(self):
        name, id, className = self.tagName.upper(), self.id, self.className
        if id and className:
            name = "%s#%s.%s" % (name, id, className)
        elif id:
            name = "%s#%s" % (name, id)
        elif className:
            name = "%s.%s" % (name, className)
        return "<%s>" % name
