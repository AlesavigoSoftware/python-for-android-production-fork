from pythonforandroid.recipe import CythonRecipe


class PyProjRecipe(CythonRecipe):
    version = 'v2.1.0rel'
    url = 'https://github.com/pyproj4/pyproj/archive/refs/tags/{version}.tar.gz'
    depends = ['setuptools']
    call_hostpython_via_targetpython = False


recipe = PyProjRecipe()
