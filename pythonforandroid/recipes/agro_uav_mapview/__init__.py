from pythonforandroid.recipe import PythonRecipe
from pathlib import Path
from typing import Union


class AgroUAVMapViewRecipe(PythonRecipe):
    url = 'https://github.com/AlesavigoSoftware/mapview-production-fork.git'

    # call_hostpython_via_targetpython = False
    install_in_hostpython = False


recipe = AgroUAVMapViewRecipe()
