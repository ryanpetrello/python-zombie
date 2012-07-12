proxy Package
=============

:mod:`client` Module
--------------------

.. automodule:: zombie.proxy.client
    :members:
    :undoc-members:
    :show-inheritance:

:mod:`server` Module
--------------------

.. automodule:: zombie.proxy.server

    .. class:: ZombieProxyServer

        .. method:: __init__(self, socket=None, wait=True)

            Spawns a node.js subprocess that listens on a TCP socket.
            A :class:`zombie.proxy.client.ZombieProxyClient` streams data to
            the server, which evaluates it as Javascript, passes it on to
            a zombie.js Browser object, and returns the results.

            :param socket: a (random, by default) filepath representing the
                           intended TCP socket location
            :param wait: when True, wait until the node.js subprocess is responsive
                        via the specified TCP socket.
