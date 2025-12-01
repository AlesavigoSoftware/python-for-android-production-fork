from pythonforandroid.recipe import CythonRecipe


class PyProjRecipe(CythonRecipe):
    version = "3.7.2"
    url = "https://github.com/pyproj4/pyproj/archive/refs/tags/{version}.tar.gz"
    depends = ["setuptools>=61.0.0", "wheel", "cython>=3.1"]
    call_hostpython_via_targetpython = False


recipe = PyProjRecipe()
