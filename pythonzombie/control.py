from pythonzombie.server import ZombieProxyServer

class Control(object):

    def __init__(self, server=None):
        if server:
            self.server = server
        else:
            self.server = ZombieProxyServer()

    def visit(self, url):
        return self.server.wait('visit', url) 

    def html(self):
        return self.server.json('browser.html()')

    def query(self, selector, context=None):
        args = ','.join(filter(None, [self.server.__encode__(selector), context]))

        js = """
            var results = [];
            var nodes = browser.querySelectorAll(%s);
            for(var i = 0; i < nodes.length; i++){
                var node = nodes[i];
                ELEMENTS.push(node);
                results.push(ELEMENTS.length - 1);
            };
            stream.end(JSON.stringify(results));
        """ % (
            args
        )
        return map(
            lambda x: DOMNode(int(x), self.server),
            self.server.__decode__(self.server.send(js))
        )


class DOMNode(object):

    def __init__(self, index, server):
        self.index = index
        self.server = server

    @property
    def tagName(self):
        return self.json('tagName').lower()

    def json(self, attr):
        return self.server.json("%s.%s" % (self.__native__, attr))

    @property
    def __native__(self):
        return "ELEMENTS[%s]" % self.index

    def __getattr__(self, name):
        return self.json(name)

    def __repr__(self):
        name, id, className = self.tagName, self.id, self.className
        if id:
            name = "%s#%s" % (name, id)
        if className:
            name = "%s.%s" % (name, className)
        return name
