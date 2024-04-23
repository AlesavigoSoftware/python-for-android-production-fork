from pythonforandroid.recipe import PythonRecipe, url_opener, url_orig_headers
from os.path import exists, isdir, join

import sh
from urllib.request import urlretrieve
from os import unlink, environ
from sys import stdout
import time
try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse

from pythonforandroid.logger import info, shprint
from pythonforandroid.util import current_directory, ensure_dir


class AgroUAVAPIRecipe(PythonRecipe):
    url = 'git+ssh://git@github.com/AlesavigoSoftware/agro-uav-api.git'

    # call_hostpython_via_targetpython = False
    install_in_hostpython = False

    def download_file(self, url, target, cwd=None):
        """
        (internal) Download an ``url`` to a ``target``.
        """
        if not url:
            return
        info('Downloading {} from {}'.format(self.name, url))

        if cwd:
            target = join(cwd, target)

        parsed_url = urlparse(url)
        if parsed_url.scheme in ('http', 'https'):
            def report_hook(index, blksize, size):
                if size <= 0:
                    progression = '{0} bytes'.format(index * blksize)
                else:
                    progression = '{0:.2f}%'.format(
                        index * blksize * 100. / float(size))
                if "CI" not in environ:
                    stdout.write('- Download {}\r'.format(progression))
                    stdout.flush()

            if exists(target):
                unlink(target)

            # Download item with multiple attempts (for bad connections):
            attempts = 0
            seconds = 1
            while True:
                try:
                    # jqueryui.com returns a 403 w/ the default user agent
                    # Mozilla/5.0 doesnt handle redirection for liblzma
                    url_opener.addheaders = [('User-agent', 'Wget/1.0')]
                    urlretrieve(url, target, report_hook)
                except OSError as e:
                    attempts += 1
                    if attempts >= 5:
                        raise
                    stdout.write('Download failed: {}; retrying in {} second(s)...'.format(e, seconds))
                    time.sleep(seconds)
                    seconds *= 2
                    continue
                finally:
                    url_opener.addheaders = url_orig_headers
                break
            return target
        elif parsed_url.scheme in ('git', 'git+file', 'git+ssh', 'git+http', 'git+https'):
            if not isdir(target):
                if url.startswith('git+'):
                    url = url[4:]
                # if 'version' is specified, do a shallow clone
                if self.version:
                    ensure_dir(target)
                    with current_directory(target):
                        shprint(sh.git, 'init')
                        shprint(sh.git, 'remote', 'add', 'origin', url)
                else:
                    shprint(sh.git, 'clone', '--branch', '1.0.5', '--single-branch', '--recursive', url, target)
            with current_directory(target):
                if self.version:
                    shprint(sh.git, 'fetch', '--depth', '1', 'origin', self.version)
                    shprint(sh.git, 'checkout', self.version)
                branch = sh.git('branch', '--show-current')
                if branch:
                    shprint(sh.git, 'pull')
                    shprint(sh.git, 'pull', '--recurse-submodules')
                shprint(sh.git, 'submodule', 'update', '--recursive', '--init', '--depth', '1')
            return target


recipe = AgroUAVAPIRecipe()
