NOTE: This is in active development and not ready for use yet.

A Python driver for Zombie.js (http://zombie.labnotes.org/) running on
top of node.js, inspired by Capybara-Zombie (https://github.com/plataformatec/capybara-zombie)::

    from pythonzombie import Browser
    b = Browser()
    b.visit('http://google.com/m').fill('input', 'Zombie.js').press_button('Search')
    assert b.location == 'http://www.google.com/m?q=Zombie.js'

Requires the latest node and zombie::

    brew install node
    curl http://npmjs.org/install.sh | sh
    npm install zombie
