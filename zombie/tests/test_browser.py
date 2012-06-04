from unittest import TestCase
import os

import fudge

from zombie import Browser
from zombie.dom import DOMNode
from zombie.proxy.client import ZombieProxyClient
from zombie.compat import urlparse


class BrowserClientTest(TestCase):
    """
    Sets up a zombie.Browser() object to test with.
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
        try {
            browser.visit("%s", function(err, browser){
                if (err)
                    stream.end(JSON.stringify(err.message));
                else
                    stream.end();
            });
        } catch (err) {
            stream.end(JSON.stringify(err.message));
        }
        """ % self.path

        with fudge.patched_context(
            ZombieProxyClient,
            'send',
            (fudge.Fake('send', expect_call=True).
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
        with open(path, 'r') as f:
            self.html = f.read()

    #
    # Document Content
    #
    def test_html(self):
        self.browser.visit(self.path)
        html = self.browser.html()
        assert '<title>Example</title>' in html
        assert '<p>This is an HTML document</p>' in html

    def test_html_with_selector(self):
        self.browser.visit(self.path)
        html = self.browser.html('#content')
        assert '<title>Example</title>' not in html
        assert '<p>This is an HTML document</p>' in html

    def test_html_with_context(self):
        self.browser.visit(self.path)
        html = self.browser.html('#content', self.browser.query('body'))
        assert '<title>Example</title>' not in html
        assert '<p>This is an HTML document</p>' in html

    def test_text(self):
        self.browser.visit(self.path)
        text = self.browser.text('title')
        assert text == 'Example'

    def test_text_no_match(self):
        self.browser.visit(self.path)
        text = self.browser.text('blink')
        assert not text

    def test_text_with_context(self):
        self.browser.visit(self.path)
        text = self.browser.text('title', self.browser.query('head'))
        assert text == 'Example'

    def test_text_with_context_missing(self):
        self.browser.visit(self.path)
        text = self.browser.text('title', self.browser.query('body'))
        assert not text

    def test_css(self):
        self.browser.visit(self.path)
        for tag in ['h1', 'p', 'form', 'input', 'button']:
            matches = self.browser.css(tag)
            assert len(matches)

    def test_css_no_results(self):
        self.browser.visit(self.path)
        matches = self.browser.css('blink')
        assert len(matches) == 0

    def test_query(self):
        self.browser.visit(self.path)
        for tag in ['h1', 'p', 'form', 'input', 'button']:
            match = self.browser.query(tag)
            assert isinstance(match, DOMNode)

    def test_query_no_results(self):
        self.browser.visit(self.path)
        match = self.browser.query('blink')
        assert match is None

    def test_by_id(self):
        matches = self.browser.visit(self.path).css('#submit')
        assert len(matches) == 1
        assert matches[0].tagName.lower() == 'button'

    def test_by_class_name(self):
        matches = self.browser.visit(self.path).css('.textfield')
        assert len(matches) == 1
        assert matches[0].tagName.lower() == 'input'

    #
    # Navigation
    #
    def test_location_get(self):
        for p in ('scheme', 'path'):
            getattr(urlparse(self.browser.visit(self.path).location), p) == \
                getattr(urlparse(self.path), p)

    def test_location_set(self):
        self.browser.location = self.path
        for p in ('scheme', 'path'):
            getattr(urlparse(self.browser.visit(self.path).location), p) == \
                getattr(urlparse(self.path), p)

    def test_click_link(self):
        self.browser.visit(self.path)
        self.browser.clickLink('#about-zombie')
        assert self.browser.location == 'http://zombie.labnotes.org/'

    def test_back(self):
        self.browser.visit('http://zombie.labnotes.org/')
        self.browser.visit('http://google.com/')
        self.browser.back()
        assert self.browser.location == 'http://zombie.labnotes.org/'

    #
    # Forms
    #
    def test_fill(self):
        self.browser.visit(self.path).fill('q', 'Zombie.js')
        assert self.browser.css('input')[0].value == 'Zombie.js'

    def test_press_button(self):
        self.browser.visit(self.path)
        self.browser.pressButton('Search')
        assert urlparse(self.browser.location).netloc == 'www.google.com'


class TestDOMNode(BrowserClientTest):

    def test_attribute_lookup(self):
        button = self.browser.visit(self.path).query('button')
        assert button.innerHTML == 'Search'

    def test_item_lookup(self):
        button = self.browser.visit(self.path).query('button')
        assert button['innerHTML'] == 'Search'

    def test_printable(self):
        self.browser.visit(self.path)

        form = self.browser.css('form')[0]
        assert repr(form) == '<FORM#form.submittable>'

        button = self.browser.css('button')[0]
        assert repr(button) == '<BUTTON#submit>'

        textfield = self.browser.css('input')[0]
        assert repr(textfield) == '<INPUT.textfield>'

        paragraph = self.browser.css('p')[0]
        assert repr(paragraph) == '<P>'

    def test_css_chaining(self):
        # The <form> contains 4 input fields
        doc = self.browser.visit(self.path)
        form = doc.css('form')[0]
        matches = form.css('input')
        assert len(matches) == 4
        for field in matches:
            assert field.tagName.lower() == 'input'

        # The document contains a paragraph, but it's *outside* of the form,
        # so it shouldn't be found under the form DOM node.
        assert 0 == len(form.css('p'))

    def test_query_chaining(self):
        doc = self.browser.visit(self.path)
        form = doc.query('form')
        button = form.query('button')
        assert button.innerHTML == 'Search'

    def test_fill(self):
        node = self.browser.visit(self.path).css('input')[0]
        assert not node.value
        node.fill('Zombie.js')
        assert node.value == 'Zombie.js'

    def test_tag_name(self):
        self.browser.visit(self.path)
        for tag in ['h1', 'p', 'form', 'input', 'button']:
            matches = self.browser.css(tag)
            assert matches[0].tagName.lower() == tag

    def test_simple_field_value(self):
        """
        <input> fields should have a toggleable value.
        """
        self.browser.visit(self.path)
        assert not self.browser.css('input')[0].value
        self.browser.css('input')[0].value = 'Zombie.js'
        assert self.browser.css('input')[0].value == 'Zombie.js'

    def test_textarea_value(self):
        """
        <textarea> fields should have a toggleable value.
        """
        self.browser.visit(self.path)
        assert self.browser.css('textarea')[0].value == ''
        self.browser.css('textarea')[0].value = 'Sample Content'
        assert self.browser.css('textarea')[0].value == 'Sample Content'

    def test_checkbox_value(self):
        """
        If a "true" value is set on a checkbox, it should become checked,
        but it's underlying `value` attribute should *not* be changed.
        """
        self.browser.visit(self.path)
        checkbox = self.browser.css('input[type="checkbox"]')[0]
        assert checkbox.value == '1'
        assert not checkbox.checked
        checkbox.value = True
        assert checkbox.value == '1'
        assert checkbox.checked
        checkbox.value = False
        assert checkbox.value == '1'
        assert not checkbox.checked

    def test_checkbox_checked(self):
        """
        Checkboxes should have a toggleable `checked` property.
        """
        self.browser.visit(self.path)
        checkbox = self.browser.css('input[type="checkbox"]')[0]
        assert not checkbox.checked
        checkbox.checked = True
        assert checkbox.checked

    def test_radiobox_value(self):
        """
        If a "true" value is set on a radio input, it should become chosen,
        but it's underlying `value` attribute should *not* be changed.
        """
        self.browser.visit(self.path)
        radios = self.browser.css('input[type="radio"]')
        assert radios[0].value == '1'
        assert radios[1].value == '2'
        assert not radios[0].checked
        assert not radios[1].checked

        radios[0].value = True
        assert radios[0].value == '1'
        assert radios[0].checked

        radios[1].value = True
        assert radios[1].value == '2'
        assert radios[1].checked
        assert not radios[0].checked

    def test_radiobox_checked(self):
        """
        Radio inputs should have a toggleable `checked` property.
        """
        self.browser.visit(self.path)
        radios = self.browser.css('input[type="radio"]')
        assert radios[0].value == '1'
        assert radios[1].value == '2'
        assert not radios[0].checked
        assert not radios[1].checked

        radios[0].checked = True
        assert radios[0].value == '1'
        assert radios[0].checked

        radios[1].checked = True
        assert radios[1].value == '2'
        assert radios[1].checked
        assert not radios[0].checked

    def test_fire(self):
        self.browser.visit(self.path)
        self.browser.css('button')[0].click()
        assert urlparse(self.browser.location).netloc == 'www.google.com'
