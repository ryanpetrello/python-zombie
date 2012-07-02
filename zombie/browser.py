from zombie.dom import BaseNode, verb
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
        raise NotImplementedError()

    def evaluate(self, expression):
        """
        Evaluates a JavaScript expression in the context of the current window
        and returns the result.
        """
        raise NotImplementedError()

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
        return self._query(selector, context, all_=False)

    def queryAll(self, selector, context=None):
        """
        Evaluate a CSS selector against the document (or an optional context
        DOMNode) and return a list of DOMNode objects.

        :param selector: a string CSS selector
                        (http://zombie.labnotes.org/selectors)
        :param context: an (optional) instance of :class:`DOMNode`
        """
        return self._query(selector, context)

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
        raise NotImplementedError()

    def reload(self, selector):
        """
        Reloads the current page.
        """
        raise NotImplementedError()

    def statusCode(self):
        """
        Returns the status code returned for this page request (200, 303, etc).
        """
        raise NotImplementedError()

    def success(self):
        """
        Returns True if the status code is 2xx.
        """
        raise NotImplementedError()

    def redirected(self):
        """
        Returns True if the page request followed a redirect.
        """
        raise NotImplementedError()

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
        Returns a debug string including Zombie version, current URL, history,
        cookies, event loop, etc.  Useful for debugging and submitting error
        reports.
        """
        raise NotImplementedError()

    @property
    def resources(self):
        """
        Returns a list of resources loaded by the browser.
        """
        raise NotImplementedError()

    def viewInBrowser(self):
        """
        Views the current document in a real Web browser. Uses the default
        system browser on OS X, BSD and Linux. Probably errors on Windows.
        """
        raise NotImplementedError()
