from pythonforandroid.recipe import PythonRecipe
from pathlib import Path
from typing import Union


class ProjectPathManager:
    PROJECT_NAME = "agro-uav-app"

    _dir_path = None

    @classmethod
    def get_project_dir_path(cls) -> Path:
        if cls._dir_path is None:

            cls._dir_path = Path()
            for folder in Path(__file__).absolute().parts:

                cls._dir_path = cls._dir_path.joinpath(folder)
                if folder == cls.PROJECT_NAME:
                    break

        return cls._dir_path

    @classmethod
    def join_str_paths(cls, *args: Union[Path, str]) -> str:
        return str(Path().joinpath(*args))


class SweetAlertRecipe(PythonRecipe):
    url = ProjectPathManager.join_str_paths(ProjectPathManager.get_project_dir_path(), 'Libs', 'sweetalert-production-fork')

    # call_hostpython_via_targetpython = False
    install_in_hostpython = False


recipe = SweetAlertRecipe()
