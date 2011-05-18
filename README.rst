NOTE: This is in active development and not ready for use yet.

A Python driver/wrapper for Zombie.js (http://zombie.labnotes.org/), inspired
by Capybara-Zombie (https://github.com/plataformatec/capybara-zombie)::

    from pythonzombie import Control
    c = Control()
    c.visit('http://example.com')
    print c.html()

Requires the latest node and zombie::

    brew install node
    brew install npm
    npm install zombie
