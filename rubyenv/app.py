import argparse
import git
import logging
import logging.config
import os
import sys

#{{{ logging config
logging.config.dictConfig({
    'version': 1,
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'default',
            'level': 'DEBUG',
            'stream': 'ext://sys.stdout',
        },
    },
    'formatters': {
        'default': {
            'format': '%(levelname)s: %(message)s',
        }
    },
})
#}}}

#{{{ subparser implementation
class subcommand(object):
    _parser = argparse.ArgumentParser()
    _subparser = _parser.add_subparsers(dest='command')
    def __new__(cls, command_or_f=None, command=None):
        if isinstance(command_or_f, basestring):
            return lambda f: subcommand(f, command_or_f)
        elif callable(command_or_f):
            return object.__new__(cls)
    def __init__(self, function, command=None):
        self.parser = self._subparser.add_parser(command or function.__name__)
        self.parser.set_defaults(function=function)
    def __call__(self, *args, **kwargs):
        return self.function(*args, **kwargs)
    def __getattr__(self, key):
        return getattr(self.parser, key)
    @classmethod
    def parse_args(cls, *args, **kwargs):
        return cls._parser.parse_args(*args, **kwargs)
    @classmethod
    def dispatch(cls, *args, **kwargs):
        ns = cls._parser.parse_args(*args, **kwargs)
        return ns.function(ns)
    @classmethod
    def set_defaults(cls, *args, **kwargs):
        cls._parser.set_defaults(*args, **kwargs)
#}}}
def get_virtualenv_dir():
    if hasattr(sys, 'real_prefix'):
        return sys.prefix
    elif hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix:
        return sys.prefix
    raise Exception('no virtualenv found')

def ensure_ruby_build():
    prefix = get_virtualenv_dir()
    parent = os.path.join(prefix, 'src')
    if not os.path.exists(parent):
        os.makedirs(parent)

    working = os.path.join(parent, 'ruby-build')
    try:
        return git.Repo(working).working_dir
    except (git.exc.NoSuchPathError, git.exc.InvalidGitRepositoryError):
        return git.Repo.clone_from('https://github.com/sstephenson/ruby-build.git', working).working_dir

@subcommand
def install(ns):
    ruby_build = os.path.join(ensure_ruby_build(), 'bin', 'ruby-build')
    os.system('%s %s %s' % (ruby_build, ns.version, get_virtualenv_dir()))
install.add_argument('version', type=str, default='stable')

@subcommand
def list(ns):
    ruby_build = os.path.join(ensure_ruby_build(), 'bin', 'ruby-build')
    os.system('%s --definitions' % ruby_build)

def main():
    subcommand.dispatch()
