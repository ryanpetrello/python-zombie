from pythonzombie.server import ZombieProxyServer

class Control(object):

    def __init__(self, server=None):
        if server:
            self.server = server
        else:
            self.server = ZombieProxyServer()

    def visit(self, url):
        return self.server.wait('visit', url) 

    def html(self, *args):
        return self.server.json('browser.html()', *args)
