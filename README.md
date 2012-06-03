A Python driver for Zombie.js (http://zombie.labnotes.org/) running on
top of node.js, inspired by Capybara-Zombie (https://github.com/plataformatec/capybara-zombie):

    from pythonzombie import Browser
    b = Browser()
    b.visit('http://google.com/m').fill('input', 'Zombie.js').pressButton('Search')
    assert b.location == 'http://www.google.com/m?q=Zombie.js'

Requires the latest node and zombie:

    brew install node
    curl http://npmjs.org/install.sh | sh
    npm install zombie

## Development

Source hosted at [GitHub](https://github.com/ryanpetrello/python-zombie). Report
issues and feature requests on [GitHub
Issues](https://github.com/ryanpetrello/python-zombie/issues).

Tests require ``tox`` and can be run with ``python setup.py test``.

All contributions must:

* Include accompanying tests.
* Include API documentation if new features or API methods are changed/added.
* Be (generally) compliant with PEP8.  One exception is that (for consistency,
  and to demonstrate their analogous nature) API methods on
  ``pythonzombie.Browser`` should follow the camel case formatting set forth in
  the zombie.js API (e.g., ``Browser.pressButton``, not
  ``Browser.press_button``).
* Not break the tests or build. Before issuing a pull request, ensure that all
  tests still pass across multiple versions of Python.
* Add your name to the (bottom of the) AUTHORS file.
