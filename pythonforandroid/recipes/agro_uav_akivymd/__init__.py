from pythonforandroid.recipe import PythonRecipe
from pathlib import Path
from typing import Union


class AkivyMDRecipe(PythonRecipe):
    url = 'https://github.com/AlesavigoSoftware/akivymd-production-fork.git'

    # call_hostpython_via_targetpython = False
    install_in_hostpython = False


recipe = AkivyMDRecipe()
