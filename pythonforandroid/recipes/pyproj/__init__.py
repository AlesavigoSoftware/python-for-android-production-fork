from pythonforandroid.recipe import CythonRecipe


class PyProjRecipe(CythonRecipe):
    version = "3.7.2"
    url = "https://github.com/pyproj4/pyproj/archive/refs/tags/{version}.tar.gz"
    depends = ["setuptools"]
    call_hostpython_via_targetpython = False


recipe = PyProjRecipe()
