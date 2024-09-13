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
    # version = '1.0.5'


recipe = AgroUAVAPIRecipe()
