import six

if six.PY2:
    from _version import __version__
    from app import main
elif six.PY3:
    from ._version import __version__
    from .app import main
