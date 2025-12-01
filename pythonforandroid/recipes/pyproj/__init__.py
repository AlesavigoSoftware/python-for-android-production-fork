from pythonforandroid.recipe import CythonRecipe


class PyProjRecipe(CythonRecipe):
    version = "3.5.0"
    url = "https://github.com/pyproj4/pyproj/archive/refs/tags/{version}.tar.gz"
    depends = ["setuptools", "wheel", "cython"]
    call_hostpython_via_targetpython = False


recipe = PyProjRecipe()
