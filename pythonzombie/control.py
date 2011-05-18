from pythonzombie.server import ZombieProxyServer

class Control(object):

    def __init__(self, server=None):
        if server:
            self.server = server
        else:
            self.server = ZombieProxyServer()

    def visit(self, url):
        return self.server.visit(url) 

    def html(self, *args):
        return self.server.method('html', *args)
