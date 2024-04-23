from pythonforandroid.recipe import PythonRecipe


class SweetAlertRecipe(PythonRecipe):
    url = 'git+ssh://git@github.com/AlesavigoSoftware/sweetalert-production-fork.git'

    # call_hostpython_via_targetpython = False
    install_in_hostpython = False


recipe = SweetAlertRecipe()
