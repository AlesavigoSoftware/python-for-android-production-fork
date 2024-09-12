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


class AgroUAVMissionKitRecipe(PythonRecipe):
    url = 'git+ssh://git@github.com/AlesavigoSoftware/agro-uav-missionkit.git'

    version = '1.4.1'

    depends = [
        'setuptools',
        'shapely',
        'matplotlib',
    ]


recipe = AgroUAVMissionKitRecipe()
