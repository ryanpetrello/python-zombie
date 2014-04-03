from unittest import TestCase
import os

from zombie.browser import Browser, DOMNode
from zombie.proxy.client import ZombieProxyClient
from zombie.compat import urlparse, PY3
from zombie.tests.webserver import WebServerTestCase


class BaseTestCase(WebServerTestCase):
    def setUp(self):
        super(BaseTestCase, self).setUp()
        self.browser = Browser()
        self.browser.visit(self.base_url)


class TestBrowser(BaseTestCase):
    #
    # BaseNode
    #
    def test_fill(self):
        self.browser.fill('q', 'Zombie.js')
        self.assertEqual(
            'Zombie.js',
            self.browser.css('input[name=q]')[0].value)

    def test_press_button(self):
        browser = self.browser
        browser.pressButton('Search')
        self.assertEqual(self.base_url + 'submit', browser.location)

    def test_check(self):
        browser = self.browser
        selector = 'input[name=mycheckbox]'

        self.assertFalse(browser.query(selector).checked)
        browser.check(selector)
        self.assertTrue(browser.query(selector).checked)

    def test_select(self):
        browser = self.browser
        selector = 'select[name=planet]'

        self.assertEqual('earth', browser.query(selector).value)
        browser.select(selector, 'Planet Mars')
        self.assertEqual('mars', browser.query(selector).value)

    def test_selectOption(self):
        browser = self.browser
        select = 'select[name=planet]'
        option = 'option[value=mars]'

        self.assertEqual('earth', browser.query(select).value)
        browser.selectOption(option)
        self.assertEqual('mars', browser.query(select).value)

    def test_unselect(self):
        browser = self.browser
        select = "select[name=colors]"
        option = "option[value=red]"

        self.assertTrue(browser.query(option).selected)
        browser.unselect(select, 'Color red')
        self.assertFalse(browser.query(option).selected)

    def test_unselectOption(self):
        browser = self.browser
        selector = "option[value=red]"

        self.assertTrue(browser.query(selector).selected)
        browser.unselectOption(selector)
        self.assertFalse(browser.query(selector).selected)

    def test_attach(self):
        browser = self.browser
        selector = 'input[name=myfile]'

        browser.attach(selector, __file__)
        files = [{
            'type': 'application/octet-stream',
            'name': os.path.basename(__file__),
            'size': os.path.getsize(__file__)}]
        self.assertEqual(files, browser.query(selector).files)

    def test_choose(self):
        browser = self.browser
        browser.choose('#color-2')
        self.assertEqual('2', browser.query('input[name=color]:checked').value)

    def test_field(self):
        field = self.browser.field('mycheckbox')
        self.assertEqual('checkbox', field.type)

    #
    # Document Content
    #
    def test_load(self):
        browser = self.browser
        browser.load("<html><head><title>Hey</title></head></html>")
        self.assertEqual('Hey', browser.query('title').text)

    def test_body(self):
        body = self.browser.body
        assert isinstance(body, DOMNode)

        html = body.innerHTML
        assert '<title>Example</title>' not in html
        assert '<p>This is an HTML document</p>' in html

    def test_html(self):
        html = self.browser.html()
        assert '<title>Example</title>' in html
        assert '<p>This is an HTML document</p>' in html

    def test_html_with_selector(self):
        html = self.browser.html('#content')
        assert '<title>Example</title>' not in html
        assert '<p>This is an HTML document</p>' in html

    def test_html_with_context(self):
        html = self.browser.html('#content', self.browser.query('body'))
        assert '<title>Example</title>' not in html
        assert '<p>This is an HTML document</p>' in html

    def test_text(self):
        text = self.browser.text('title')
        assert text == 'Example'

    def test_text_no_match(self):
        text = self.browser.text('blink')
        assert not text

    def test_text_with_context(self):
        text = self.browser.text('title', self.browser.query('head'))
        assert text == 'Example'

    def test_text_with_context_missing(self):
        text = self.browser.text('title', self.browser.query('body'))
        assert not text

    def test_css(self):
        for tag in ['h1', 'p', 'form', 'input', 'button']:
            matches = self.browser.css(tag)
            assert len(matches)

    def test_css_no_results(self):
        matches = self.browser.css('blink')
        self.assertEqual(0, len(matches))

    def test_query(self):
        for tag in ['h1', 'p', 'form', 'input', 'button']:
            match = self.browser.query(tag)
            assert isinstance(match, DOMNode)

    def test_query_no_results(self):
        match = self.browser.query('blink')
        self.assertIsNone(match)

    def test_by_id(self):
        matches = self.browser.css('#submit')
        assert len(matches) == 1
        assert matches[0].tagName.lower() == 'button'

    def test_by_class_name(self):
        matches = self.browser.css('.textfield')
        assert len(matches) == 1
        assert matches[0].tagName.lower() == 'input'

    #
    # Navigation
    #
    def test_location_get(self):
        for p in ('scheme', 'path'):
            getattr(urlparse(self.browser.location), p) == \
                getattr(urlparse(self.base_url), p)

    def test_location_set(self):
        url = self.base_url + 'location2'
        self.browser.location = url
        for p in ('scheme', 'path'):
            getattr(urlparse(self.browser.visit(url).location), p) == \
                getattr(urlparse(url), p)

    def test_click_link(self):
        browser = self.browser
        browser.clickLink('#about-zombie')
        self.assertEqual(self.base_url + 'location2', browser.location)

    def test_link_by_selector(self):
        match = self.browser.link('#about-zombie')
        assert isinstance(match, DOMNode)

        assert match.innerHTML == 'Learn About Zombie'

    def test_link_by_inner_text(self):
        match = self.browser.link('Learn About Zombie')
        assert isinstance(match, DOMNode)

        assert match.id == 'about-zombie'

    def test_back(self):
        browser = self.browser
        browser.clickLink('#about-zombie')
        self.assertTrue(browser.location.endswith('location2'))
        browser.back()
        self.assertEqual(self.browser.location, self.base_url)

    def test_reload(self):
        self.browser.fill('q', 'Zombie.js')
        assert self.browser.css('input')[0].value == 'Zombie.js'

        self.browser.reload()
        assert self.browser.css('input')[0].value == ''

    def test_status_code_200(self):
        assert self.browser.statusCode == 200

    def test_success(self):
        assert self.browser.success is True

    #
    # Forms
    #
    #
    # Debugging
    #

    def test_get_resource(self):
        res = self.browser.get_resource('/location2')
        self.assertEqual(200, res['statusCode'])

    def test_post_resource(self):
        res = self.browser.post_resource('/submit', {})
        self.assertIn('Submitted', res['body'])

    def test_evaluate(self):
        self.assertEqual(2, self.browser.evaluate('1+1'))

    def test_wait(self):
        self.browser.wait()

    def test_resources(self):
        resources = self.browser.resources
        assert len(resources)
        for r in resources:
            assert r['method']
            assert r['url']
            assert r['statusCode']
            assert r['statusText']
            assert r['time']

    def test_not_redirected(self):
        self.assertIn('<title>Example', self.browser.html())
        self.assertFalse(self.browser.redirected)

    def test_redirected(self):
        self.browser.visit(self.base_url + 'redirect')
        self.assertIn('<title>Example', self.browser.html())
        self.assertTrue(self.browser.redirected)


class TestDOMNode(BaseTestCase):
    def test_attribute_lookup(self):
        button = self.browser.query('button')
        assert button.innerHTML == 'Search'

    def test_text_content(self):
        btn = self.browser.query('button')
        assert btn.textContent == btn.innerText == btn.text == 'Search'

    def test_html_content(self):
        btn = self.browser.query('button')
        assert btn.innerHTML == btn.html == 'Search'

    def test_item_lookup(self):
        button = self.browser.query('button')
        assert button['innerHTML'] == 'Search'

    def test_printable(self):
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
        form = self.browser.css('form')[0]
        inputs = form.css('input')

        self.assertEqual(6, len(inputs))
        self.assertTrue(all(f.tagName.lower() == 'input' for f in inputs))

        # The document contains a paragraph, but it's *outside* of the form,
        # so it shouldn't be found under the form DOM node.
        self.assertEqual([], form.css('p'))

    def test_query_chaining(self):
        form = self.browser.query('form')
        button = form.query('button')
        assert button.innerHTML == 'Search'

    def test_fill(self):
        node = self.browser.css('input')[0]
        assert not node.value
        node.fill('Zombie.js')
        assert node.value == 'Zombie.js'

    def test_tag_name(self):
        for tag in ['h1', 'p', 'form', 'input', 'button']:
            matches = self.browser.css(tag)
            assert matches[0].tagName.lower() == tag

    def test_simple_field_value(self):
        """
        <input> fields should have a toggleable value.
        """
        assert not self.browser.css('input')[0].value
        self.browser.css('input')[0].value = 'Zombie.js'
        assert self.browser.css('input')[0].value == 'Zombie.js'

    def test_textarea_value(self):
        """
        <textarea> fields should have a toggleable value.
        """
        assert self.browser.css('textarea')[0].value == ''
        self.browser.css('textarea')[0].value = 'Sample Content'
        assert self.browser.css('textarea')[0].value == 'Sample Content'

    def test_checkbox_value(self):
        """
        If a "true" value is set on a checkbox, it should become checked,
        but it's underlying `value` attribute should *not* be changed.
        """
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
        checkbox = self.browser.css('input[type="checkbox"]')[0]
        assert not checkbox.checked
        checkbox.checked = True
        assert checkbox.checked

    def test_radiobox_value(self):
        """
        If a "true" value is set on a radio input, it should become chosen,
        but it's underlying `value` attribute should *not* be changed.
        """
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
        self.browser.css('button')[0].click()
        assert urlparse(self.browser.location).path.endswith('/submit')

    def test_pressButton(self):
        self.browser.query('#submit').pressButton()
        self.assertTrue(self.browser.location.endswith('/submit'))

    def test_check(self):
        element = self.browser.query('input[name=mycheckbox]')
        element.check()
        self.assertTrue(element.checked)

    def test_uncheck(self):
        element = self.browser.query('input[name=mycheckedcheckbox]')
        self.assertTrue(element.checked)
        element.uncheck()
        self.assertFalse(element.checked)

    def test_select(self):
        element = self.browser.query('select[name=planet]')
        element.select('Planet Mars')
        self.assertTrue(self.browser.query('option[value=mars]').selected)

    def test_selectOption(self):
        element = self.browser.query('option[value=mars]')
        element.selectOption()
        self.assertTrue(element.selected)

    def test_unselect(self):
        element = self.browser.query('select[name=colors]')
        element.unselect('Color red')
        self.assertFalse(self.browser.query('option[value=red]').selected)

    def test_attach(self):
        element = self.browser.query('input[name=myfile]')

        element.attach(__file__)
        files = [{
            'type': 'application/octet-stream',
            'name': os.path.basename(__file__),
            'size': os.path.getsize(__file__)}]
        self.assertEqual(files, element.files)

    def test_choose(self):
        browser = self.browser
        browser.query('#color-2').choose()
        self.assertEqual('2', browser.query('input[name=color]:checked').value)

    def test_field(self):
        element = self.browser.query('body')
        self.assertIs(element, element.field())
