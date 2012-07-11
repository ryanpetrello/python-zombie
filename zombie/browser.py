from zombie.dom import BaseNode, DOMNode, verb
from zombie.proxy.server import ZombieProxyServer
from zombie.proxy.client import ZombieProxyClient

__all__ = ['Browser']


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
        self.server = server
        self.client = ZombieProxyClient(server.socket)

    #
    # Document Content
    #
    @property
    def body(self):
        """
        Returns the body element of the current document.
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
        Returns the HTML content of the current document.

        :param selector: an optional string CSS selector
                        (http://zombie.labnotes.org/selectors)
        :param context: an (optional) instance of :class:`DOMNode`
        """
        return self._with_context('html', selector, context)

    def query(self, selector, context=None):
        """
        Evaluate a CSS selector against the document (or an optional context
        DOMNode) and return a single DOMNode object.

        :param selector: a string CSS selector
                        (http://zombie.labnotes.org/selectors)
        :param context: an (optional) instance of :class:`DOMNode`
        """
        return self._node('query', selector, context)

    def queryAll(self, selector, context=None):
        """
        Evaluate a CSS selector against the document (or an optional context
        DOMNode) and return a list of DOMNode objects.

        :param selector: a string CSS selector
                        (http://zombie.labnotes.org/selectors)
        :param context: an (optional) instance of :class:`DOMNode`
        """
        return self._nodes('queryAll', selector, context)

    def css(self, selector, context=None):
        """
        An alias for Browser.queryAll.

        :param selector: a string CSS selector
                        (http://zombie.labnotes.org/selectors)
        :param context: an (optional) instance of :class:`DOMNode`
        """
        return self.queryAll(selector, context)

    def text(self, selector, context=None):
        """
        Returns the text content of specific elements

        :param selector: a string CSS selector
                        (http://zombie.labnotes.org/selectors)
        :param context: an (optional) instance of :class:`DOMNode`
        """
        return self._with_context('text', selector, context)

    #
    # Navigation
    #
    @verb
    def clickLink(self, selector):
        self.client.wait('clickLink', selector)

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

    @verb
    def back(self):
        self.client.wait('back')

    def link(self, selector):
        """
        Finds and returns a link <a> element. You can use a CSS selector or
        find a link by its text contents (case sensitive, but ignores
        leading/trailing spaces).
        """
        return self._node('link', selector, None)

    def reload(self):
        """
        Reloads the current page.
        """
        return self.client.wait('reload')

    @property
    def statusCode(self):
        """
        Returns the status code returned for this page request (200, 303, etc).
        """
        return self.client.json('browser.statusCode')

    @property
    def success(self):
        """
        Returns True if the status code is 2xx.
        """
        return self.client.json('browser.success')

    @property
    def redirected(self):
        """
        Returns True if the page request followed a redirect.
        """
        return self.client.json('browser.redirected')

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
    def pressButton(self, selector):
        """
        Press a specific button (by innerText or CSS selector in the current
        document.
        """
        self.client.wait('pressButton', selector)

    #
    # Debugging
    #
    def dump(self):
        """
        Prints a debug string including Zombie version, current URL, history,
        cookies, event loop, etc.  Useful for debugging and submitting error
        reports.
        """
        self.client.json('browser.dump()')

    @property
    def resources(self):
        """
        Returns a list of resources loaded by the browser.
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
