NOTE: This is in active development and not ready for use yet.

For those following, this project is *not* dead - I'm currently at a roadblock
until @assaf includes a bug fix of mine in a stable release of Zombie.js:

https://github.com/assaf/zombie/pull/150

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
