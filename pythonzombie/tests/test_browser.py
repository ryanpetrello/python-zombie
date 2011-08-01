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

    def test_css(self):
        self.browser.visit(self.path)
        for tag in ['h1', 'p', 'form', 'input', 'button']:
            matches = self.browser.css(tag)
            assert len(matches)

    def test_by_id(self):
        matches = self.browser.visit(self.path).css('#submit')
        assert len(matches) == 1
        assert matches[0].tagName.lower() == 'button'

    def test_by_class_name(self):
        matches = self.browser.visit(self.path).css('.textfield')
        assert len(matches) == 1
        assert matches[0].tagName.lower() == 'input'

    def test_location_get(self):
        assert self.browser.visit(self.path).location['href'] == self.path

    def test_location_set(self):
        self.browser.location = self.path
        assert self.browser.visit(self.path).location['href'] == self.path

    def test_fill(self):
        self.browser.visit(self.path).fill('q', 'Zombie.js')
        assert self.browser.css('input')[0].value == 'Zombie.js'

    def test_press_button(self):
        self.browser.visit(self.path)
        assert self.browser.location['hash'] == ''
        self.browser.pressButton('Search')
        assert self.browser.location['hash'] == '#submit'


class TestDOMNode(BrowserClientTest):

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
        form = self.browser.visit(self.path).css('form')[0]
        matches = form.css('input')
        assert len(matches) == 4
        for field in matches:
            field.tagName.lower() == 'input'

        # The document contains a paragraph, but it's *outside* of the form,
        # so it shouldn't be found under the form DOM node.
        assert len(form.css('p')) == 0

    def test_fill(self):
        node = self.browser.visit(self.path).css('input')[0]
        assert node.value == ''
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
        assert self.browser.css('input')[0].value == ''
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
        assert checkbox.checked == False
        checkbox.value = True
        assert checkbox.value == '1'
        assert checkbox.checked == True
        checkbox.value = False
        assert checkbox.value == '1'
        assert checkbox.checked == False

    def test_checkbox_checked(self):
        """
        Checkboxes should have a toggleable `checked` property.
        """
        self.browser.visit(self.path)
        checkbox = self.browser.css('input[type="checkbox"]')[0]
        assert checkbox.checked == False
        checkbox.checked = True
        assert checkbox.checked == True

    def test_radiobox_value(self):
        """
        If a "true" value is set on a radio input, it should become chosen,
        but it's underlying `value` attribute should *not* be changed.
        """
        self.browser.visit(self.path)
        radios = self.browser.css('input[type="radio"]')
        assert radios[0].value == '1'
        assert radios[1].value == '2'
        assert radios[0].checked == False
        assert radios[1].checked == False

        radios[0].value = True
        assert radios[0].value == '1'
        assert radios[0].checked == True

        radios[1].value = True
        assert radios[1].value == '2'
        assert radios[1].checked == True
        assert radios[0].checked == False

    def test_radiobox_checked(self):
        """
        Radio inputs should have a toggleable `checked` property.
        """
        self.browser.visit(self.path)
        radios = self.browser.css('input[type="radio"]')
        assert radios[0].value == '1'
        assert radios[1].value == '2'
        assert radios[0].checked == False
        assert radios[1].checked == False

        radios[0].checked = True
        assert radios[0].value == '1'
        assert radios[0].checked == True

        radios[1].checked = True
        assert radios[1].value == '2'
        assert radios[1].checked == True
        assert radios[0].checked == False

    def test_fire(self):
        self.browser.visit(self.path)
        assert self.browser.location['hash'] == ''
        self.browser.css('button')[0].click()
        assert self.browser.location['hash'] == '#submit'
