from pythonzombie.server import ZombieProxyServer

class Queryable(object):

    def __query__(self, selector, context=None):
        args = ','.join(filter(None, [self.__encode__(selector), context]))

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
            self.__decode__(self.server.send(js))
        )

    def __encode__(self, value):
        return self.server.__encode__(value)

    def __decode__(self, value):
        return self.server.__decode__(value)


class Browser(Queryable):

    def __init__(self, server=None):
        if server:
            self.server = server
        else:
            self.server = ZombieProxyServer()

    def visit(self, url):
        return self.server.wait('visit', url) 

    def html(self):
        return self.server.json('browser.html()')

    def css(self, selector, context=None):
        return self.__query__(selector, context)


class DOMNode(Queryable):

    def __init__(self, index, server):
        self.index = index
        self.server = server

    def css(self, selector):
        return self.__query__(selector, self.__native__)

    #
    # Attribute (normal and specialized)
    # access methods.
    # 
    @property
    def tagName(self):
        return self.json('tagName').lower()
    
    @property
    def value(self):
        if self.tagName == 'textarea':
            return self.textContent
        return self.json('value')

    @value.setter
    def value(self, value):
        js = """
            var node = %(native)s;
            var tagName = node.tagName;
            if(tagName == "TEXTAREA"){
              node.textContent = %(value)s;
            }else{
                var type = node.getAttribute('type');
                if(type == "checkbox"){
                    %(value)s ? browser.check(node) : browser.uncheck(node);
                }else if(type == "radio"){
                    browser.choose(node);
                }else{
                    browser.fill(node, %(value)s);
                }
            }
            stream.end();
        """ % {
            'native'    : self.__native__,
            'value'     : self.__encode__(value)
        }

        self.server.send(js)

    def json(self, attr):
        return self.server.json("%s.%s" % (self.__native__, attr))

    def __getattr__(self, name):
        return self.json(name)

    #
    # Events
    #
    def click(self):
        self.server.wait('fire', 'click', self)

    #
    # Private methods
    #
    @property
    def __native__(self):
        return "ELEMENTS[%s]" % self.index

    def __repr__(self):
        name, id, className = self.tagName, self.id, self.className
        if id:
            name = "%s#%s" % (name, id)
        if className:
            name = "%s.%s" % (name, className)
        return "<%s>" % name

    @property
    def __json__(self):
        return self.__native__
