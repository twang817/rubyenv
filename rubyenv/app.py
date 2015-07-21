import argparse
import git
import logging
import logging.config
import os
import shutil
import sys
import tarfile
import urllib2
import urlparse

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

def _get_prebuilt_list():
    import platform

    system = platform.system()
    if system == 'Linux':
        machine = platform.machine()
        distro, vers, _ = platform.linux_distribution()
        distro = distro.lower()

    for url in urllib2.urlopen('https://raw.githubusercontent.com/rvm/rvm/master/config/remote').read().splitlines():
        url = urlparse.urlparse(url)
        path = url.path.split('/')
        if distro in path and vers in path and machine in path:
            ver = path[-1]
            ver, _ = os.path.splitext(ver)
            ver, _ = os.path.splitext(ver)
            ver = ver.split('-')[1:]
            ver = '-'.join(ver)
            yield ver, url

def _get_numerical_version(ver):
    ver = ver.split('-')
    ver, patch = ver[0], ver[1:]
    ver = ver.split('.')
    if patch:
        patch = patch[0][1:]
        ver.append(patch)
    else:
        ver.append(0)
    return ver

def _copytree(src, dst):
    if not os.path.exists(dst):
        os.makedirs(dst)
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.islink(s):
            if os.path.lexists(d) or os.path.isfile(d):
                os.remove(d)
            elif os.path.isdir(d):
                shutil.rmtree(d)
            os.symlink(os.readlink(s), d)
        elif os.path.isdir(s):
            _copytree(s, d)
        else:
            try:
                shutil.copy(s, d)
            except IOError as e:
                os.remove(d)
                shutil.copy(s, d)

@subcommand
def install(ns):
    if ns.prebuilt:
        try:
            for ver, url in sorted(_get_prebuilt_list(), key=lambda (v, u): _get_numerical_version(v)):
                if ver == ns.version:
                    break
            else:
                if ns.version != 'latest':
                    print 'could not find version', ns.version
                    sys.exit(1)

            tarname = os.path.basename(url.path)
            base, _ = os.path.splitext(tarname)
            base, _ = os.path.splitext(base)
            tarpath = os.path.join(get_virtualenv_dir(), 'src', tarname)
            extractdir = os.path.dirname(tarpath)
            extractpath = os.path.join(extractdir, base)

            resp = urllib2.urlopen(urlparse.urlunparse(url))
            content = resp.read()
            with open(tarpath, 'wb') as f:
                f.write(content)

            if os.path.exists(extractpath):
                shutil.rmtree(extractpath)
            t = tarfile.open(tarpath)
            t.extractall(extractdir)
            t.close()

            _copytree(extractpath, get_virtualenv_dir())

            cachedir = os.path.join(get_virtualenv_dir(), 'lib', 'ruby', 'gems', '2.2.0', 'cache')
            os.unlink(cachedir)
            os.mkdir(cachedir)
            return
        except Exception as e:
            print 'Could not install prebuilt binary', e
            import traceback
            traceback.print_exc()
            sys.exit(1)
    ruby_build = os.path.join(ensure_ruby_build(), 'bin', 'ruby-build')
    os.system('%s %s %s' % (ruby_build, ns.version, get_virtualenv_dir()))
install.add_argument('version', type=str, nargs='?', default='latest')
install.add_argument('--prebuilt', action='store_true')

@subcommand('list')
def _list(ns):
    if ns.prebuilt:
        try:
            for ver, url in _get_prebuilt_list():
                print ver
            return
        except Exception as e:
            print 'Could not load prebuilt list', e
            sys.exit(1)
    ruby_build = os.path.join(ensure_ruby_build(), 'bin', 'ruby-build')
    os.system('%s --definitions' % ruby_build)
_list.add_argument('--prebuilt', action='store_true')

def main():
    subcommand.dispatch()
