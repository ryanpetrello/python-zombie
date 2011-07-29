from pythonzombie.proxy.client  import ZombieProxyClient
from pythonzombie               import Browser
from unittest                   import TestCase

import fudge
import os


class BrowserClientTest(TestCase):
    """
    Sets up a pythonzombie.Browser() object to test with.
    """

    def setUp(self):
        super(BrowserClientTest, self).setUp()
        self.browser = Browser()
       
        # Build the path to the example.html file
        path = os.path.dirname(os.path.abspath(__file__)) 
        path = os.path.join(path, 'helpers', 'example.html')
        self.path = 'file://%s' % path

    def tearDown(self):
        super(BrowserClientTest, self).tearDown()
        fudge.clear_expectations()


class TestServerCommunication(BrowserClientTest):

    @fudge.with_fakes
    def test_visit(self):

        js = """
        browser.visit("%s", function(err, browser){
            if(err)
                stream.end(JSON.stringify(err.stack));
            else    
                stream.end();
        });
        """ % self.path

        with fudge.patched_context(
            ZombieProxyClient,
            '__send__',
            (fudge.Fake('__send__', expect_call=True).
                with_args(js)
            )):

            assert self.browser.visit(self.path) == self.browser

class TestBrowser(BrowserClientTest):

    def setUp(self):
        super(TestBrowser, self).setUp()
        self.browser = Browser()
       
        # Build the path to the example.html file
        path = os.path.dirname(os.path.abspath(__file__)) 
        path = os.path.join(path, 'helpers', 'example.html')
        self.path = 'file://%s' % path
        self.html = open(path, 'r').read()

    def test_html(self):
        assert '<p>This is an HTML document</p>' in self.browser.visit(
            self.path
        ).html

    def test_html(self):
        assert '<p>This is an HTML document</p>' in self.browser.visit(
            self.path
        ).html

    def test_location_get(self):
        assert self.browser.visit(self.path).location['href'] == self.path

    def test_location_set(self):
        self.browser.location = self.path
        assert self.browser.visit(self.path).location['href'] == self.path

    def test_css(self):
        for tag in ['h1', 'p', 'form', 'input', 'button']:
            matches = self.browser.visit(self.path).css(tag)
            assert len(matches) == 1
            assert matches[0].tagName.lower() == tag

    def test_fill(self):
        self.browser.visit(self.path).fill('q', 'Zombie.js')
        assert self.browser.css('input')[0].value == 'Zombie.js'

    def test_press_button(self):
        self.browser.visit(self.path)
        assert self.browser.location['hash'] == ''
        self.browser.pressButton('Search')
        assert self.browser.location['hash'] == '#submit'


class TestDOMNode(BrowserClientTest):
    pass
