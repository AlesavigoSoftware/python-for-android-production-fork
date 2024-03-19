from pythonforandroid.recipe import PythonRecipe
from pathlib import Path
from typing import Union
from os.path import basename, dirname, exists, isdir, isfile, join, realpath, split
import glob

import hashlib
from re import match

import sh
import shutil
import fnmatch
import urllib.request
from urllib.request import urlretrieve
from os import listdir, unlink, environ, curdir, walk
from sys import stdout
import time

import packaging.version

from pythonforandroid.logger import logger, info, warning, debug, shprint, info_main
from pythonforandroid.util import current_directory, ensure_dir, BuildInterruptingException, rmdir, move, touch
from pythonforandroid.util import load_source as import_recipe


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


class AgroUAVMissionKitRecipe(PythonRecipe):
    url = ProjectPathManager.join_str_paths(ProjectPathManager.get_project_dir_path(), 'Libs', 'agro-uav-missionkit')

    depends = [
        'setuptools',
        'shapely',
        'matplotlib',
    ]

    def build_arch(self, arch):
        """Install the Python module by calling setup.py install with
        the target Python dir."""
        # print('*' * 30)
        # self.install_python_package(arch, 'shapely', env=self.get_recipe_env(arch))
        # print('*' * 30)
        super().build_arch(arch)

    def install_python_package(self, arch, name=None, env=None, is_dir=True):
        """Automate the installation of a Python package (or a cython
        package where the cython components are pre-built)."""
        if name is None:
            name = self.name
        if env is None:
            env = self.get_recipe_env(arch)

        info('Installing {} into site-packages'.format(self.name))

        hostpython = sh.Command(self.hostpython_location)
        hpenv = env.copy()
        with current_directory(self.get_build_dir(arch.arch)):
            shprint(hostpython, 'setup.py', 'install', '-O2',
                    '--root={}'.format(self.ctx.get_python_install_dir(arch.arch)),
                    '--install-lib=.',
                    _env=hpenv, *self.setup_extra_args)

            # If asked, also install in the hostpython build dir
            if self.install_in_hostpython:
                self.install_hostpython_package(arch)


recipe = AgroUAVMissionKitRecipe()
