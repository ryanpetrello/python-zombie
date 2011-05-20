from pythonzombie.server        import ZombieProxyServer
from pythonzombie.browser       import Browser
from unittest                   import TestCase

import fudge
import os

class TestServerCommunication(TestCase):
    
    def setUp(self):
        super(TestServerCommunication, self).setUp()
        self.browser = Browser()
       
        # Build the path to the example.html file
        path = os.path.dirname(os.path.abspath(__file__)) 
        path = os.path.join(path, 'helpers', 'example.html')
        self.path = 'file://localhost:80%s' % path
        print self.path

    def tearDown(self):
        super(TestServerCommunication, self).tearDown()
        fudge.clear_expectations()

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
            ZombieProxyServer,
            '__send__',
            (fudge.Fake('__send__', expect_call=True).
                with_args(js)
            )):

            self.browser.visit(self.path)
