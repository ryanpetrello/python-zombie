import sys

# True if we are running on Python 3.
PY3 = sys.version_info[0] == 3

if PY3:  # pragma: nocover
    from io import BytesIO as StringIO
    from urllib.parse import urlparse
else:  # pragma: nocover
    from urlparse import urlparse  # noqa
    from cStringIO import StringIO  # noqa
