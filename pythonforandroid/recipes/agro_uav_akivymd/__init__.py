from pythonforandroid.recipe import PythonRecipe


class AkivyMDRecipe(PythonRecipe):
    url = 'git+ssh://git@github.com/AlesavigoSoftware/akivymd-production-fork.git'

    # call_hostpython_via_targetpython = False
    install_in_hostpython = False


recipe = AkivyMDRecipe()
