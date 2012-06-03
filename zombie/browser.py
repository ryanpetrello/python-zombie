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
