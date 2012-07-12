from zombie.dom import BaseNode, DOMNode
from zombie.proxy.server import ZombieProxyServer
from zombie.proxy.client import ZombieProxyClient

__all__ = ['Browser']


class Browser(BaseNode):
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
    # Document Content
    #
    @property
    def body(self):
        """
        Returns a :class:`zombie.dom.DOMNode` representing the body element of
        the current document.
        """

        js = """
            ELEMENTS.push(browser.body);
            stream.end(JSON.stringify(ELEMENTS.length - 1));
        """

        #
        # Translate the reference into a DOMNode object which can be used to
        # make subsequent object/attribute lookups later.
        #
        decoded = self.decode(self.client.send(js))
        return DOMNode(decoded, self.client)

    def html(self, selector='html', context=None):
        """
        Returns the HTML content (string) of the current document.

        :param selector: an optional string CSS selector
                        (http://zombie.labnotes.org/selectors)
        :param context: an (optional) instance of :class:`zombie.dom.DOMNode`
        """
        return self._with_context('html', selector, context)

    def query(self, selector, context=None):
        """
        Evaluate a CSS selector against the document (or an optional context
        :class:`zombie.dom.DOMNode`) and return a single
        :class:`zombie.dom.DOMNode` object.

        :param selector: a string CSS selector
                        (http://zombie.labnotes.org/selectors)
        :param context: an (optional) instance of :class:`zombie.dom.DOMNode`
        """
        return self._node('query', selector, context)

    def queryAll(self, selector, context=None):
        """
        Evaluate a CSS selector against the document (or an optional context
        :class:`zombie.dom.DOMNode`) and return a list of
        :class:`zombie.dom.DOMNode` objects.

        :param selector: a string CSS selector
                        (http://zombie.labnotes.org/selectors)
        :param context: an (optional) instance of :class:`zombie.dom.DOMNode`
        """
        return self._nodes('queryAll', selector, context)

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
        return self._with_context('text', selector, context)

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
        self.client.wait('clickLink', selector)
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
        self.client.wait('visit', url)
        return self

    def back(self):
        """
        Navigate to the previous page in history.

        Returns the :class:`zombie.browser.Browser` to allow function chaining.
        """
        self.client.wait('back')
        return self

    def link(self, selector):
        """
        Finds and returns a link ``<a>`` element (:class:`zombie.dom.DOMNode`).
        You can use a CSS selector or find a link by its text contents (case
        sensitive, but ignores leading/trailing spaces).

        :param selector: an optional string CSS selector
                        (http://zombie.labnotes.org/selectors) or inner text
        """
        return self._node('link', selector, None)

    def reload(self):
        """
        Reloads the current page.

        Returns the :class:`zombie.browser.Browser` to allow function chaining.
        """
        self.client.wait('reload')
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

    #
    # Forms
    #
    def fill(self, field, value):
        """
        Fill a specified form field in the current document.

        :param field: an instance of :class:`zombie.dom.DOMNode`
        :param value: any string value

        Returns the :class:`zombie.browser.Browser` to allow function chaining.
        """
        self._fill(field, value)
        return self

    def pressButton(self, selector):
        """
        Press a specific button (by innerText or CSS selector) in the current
        document.

        Returns the :class:`zombie.browser.Browser` to allow function chaining.
        """
        self.client.wait('pressButton', selector)
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

    @property
    def resources(self):
        """
        Returns a list of resources loaded by the browser, e.g.,
        ::
            [{
                'url': '...',
                'time': '...ms',
                'size': '...kb',
                'request': '...',
                'response': '...'
            }]
        """
        js = """
            var resources = browser.resources.map(
                function(r){
                    return {
                        'url': r.url,
                        'time': r.time + 'ms',
                        'size': r.size / 1024 + 'kb',
                        'request': r.request.toString(),
                        'response': r.request.toString()
                    }
                }
            );
            stream.end(JSON.stringify(resources))
        """
        return self.decode(self.client.send(js))

    def viewInBrowser(self):
        """
        Views the current document in a real Web browser. Uses the default
        system browser on OS X, BSD and Linux. Probably errors on Windows.
        """
        return self.client.send('browser.viewInBrowser()')  # pragma: nocover
