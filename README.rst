Anthony Longs copy of this project.

Recent Changes:
    Removed console print statements.
    Included the server.js file which was previously missing from the install config, and not let this module work after installed.

###

NOTE: This is in active development and not ready for use yet.

A Python driver for Zombie.js (http://zombie.labnotes.org/) running on
top of node.js, inspired by Capybara-Zombie (https://github.com/plataformatec/capybara-zombie)::

    from pythonzombie import Browser
    b = Browser()
    b.visit('http://google.com/m').fill('input', 'Zombie.js').pressButton('Search')
    assert b.location['href'] == 'http://www.google.com/m?q=Zombie.js'

Requires the latest node and zombie::

    brew install node
    brew install npm
    npm install zombie
