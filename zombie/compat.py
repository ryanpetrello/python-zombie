import sys

# True if we are running on Python 3.
PY3 = sys.version_info[0] == 3
PY26 = sys.version_info[0] == 2 and sys.version_info[1] == 6

if PY3:
    from io import BytesIO as StringIO
    from urllib.parse import urlparse
else:
    from urlparse import urlparse  # noqa
    from cStringIO import StringIO  # noqa

if PY26:
    from unittest2 import TestCase
else:
    from unittest import TestCase

if PY3:
    def to_bytes(string):
        return bytes(string, 'utf-8')
else:
    to_bytes = lambda s: s
