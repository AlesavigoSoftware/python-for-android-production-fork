from pythonforandroid.recipe import PythonRecipe


class AgroUAVMapViewRecipe(PythonRecipe):
    url = 'git+ssh://git@github.com/AlesavigoSoftware/mapview-production-fork.git'

    # call_hostpython_via_targetpython = False
    install_in_hostpython = False


recipe = AgroUAVMapViewRecipe()
