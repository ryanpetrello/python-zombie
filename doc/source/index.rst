.. zombie documentation master file, created by
   sphinx-quickstart on Sun Jun  3 14:04:52 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to zombie's documentation!
========================================

Zombie is a Python driver for Zombie.js (http://zombie.labnotes.org/), a headless browser
powered by node.js (http://nodejs.org)::

    from zombie import Browser
    browser = Browser()

    # Fill email and password, then submit form
    browser.visit("http://localhost:8080/").fill(
        "email",
        "zombie@underworld.dead"
    ).fill(
        "password",
        "eat-the-living"
    ).pressButton(
        "Sign Me Up!"
    )

    assert browser.success
    assert browser.text("title") == "Welcome to Brains Depot"

As much as possible, the methods of :class:`zombie.browser.Browser` are
analogous to the methods of Zombie.js' ``Browser`` class
(http://zombie.labnotes.org/API).

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

