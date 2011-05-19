NOTE: This is in active development and not ready for use yet.

A Python driver for Zombie.js (http://zombie.labnotes.org/) running on
top of node.js, inspired by Capybara-Zombie (https://github.com/plataformatec/capybara-zombie)::

    from pythonzombie import Browser
    browser = Browser()
    browser.visit('http://google.com/m')
    browser.fill('input', 'Zombie.js').pressButton('Search')
    assert browser.location['href'] == 'http://www.google.com/m?q=Zombie.js'

Requires the latest node and zombie::

    brew install node
    brew install npm
    npm install zombie
