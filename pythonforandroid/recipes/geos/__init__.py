from os.path import join, exists
import os

import sh
from pythonforandroid.recipe import Recipe
from pythonforandroid.toolchain import current_directory, shprint


class GeosRecipe(Recipe):
    """
    Рецепт для сборки C/C++ библиотеки GEOS под Android.
    Используем CMake, как в официальной документации GEOS.
    """

    name = "geos"
    # версия, совместимая с Shapely 2.1.x (wheels включают 3.13.1)
    version = "3.13.1"
    url = "https://download.osgeo.org/geos/geos-{version}.tar.bz2"

    # если нужны доп. зависимости (zlib и т.п.), добавь их сюда:
    # depends = ["zlib"]

    def get_install_prefix(self, arch):
        # сюда будет выполнен `make install`
        return join(self.get_build_dir(arch.arch), "install")

    def get_geos_env(self, arch):
        """
        Хелпер, чтобы Shapely мог взять пути к include/lib в формате,
        который ожидает официальный инстал-гайд Shapely.
        """
        prefix = self.get_install_prefix(arch)
        include_dir = join(prefix, "include")
        lib_dir = join(prefix, "lib")
        # на некоторых тулчейнах может быть lib64, учти это, если что
        if not exists(lib_dir):
            lib64_dir = join(prefix, "lib64")
            if exists(lib64_dir):
                lib_dir = lib64_dir

        return {
            "GEOS_INCLUDE_PATH": include_dir,
            "GEOS_LIBRARY_PATH": lib_dir,
        }

    def build_arch(self, arch):
        super().build_arch(arch)
        env = self.get_recipe_env(arch)
        build_dir = self.get_build_dir(arch.arch)
        src_dir = f"geos-{self.version}"
        install_prefix = self.get_install_prefix(arch)

        with current_directory(build_dir):
            # исходники уже распакованы p4a в каталог geos-{version}
            with current_directory(src_dir):
                build_subdir = "_build"
                if not exists(build_subdir):
                    os.makedirs(build_subdir)
                with current_directory(build_subdir):
                    # базовая CMake-сборка из официального гайда GEOS
                    # https://libgeos.org/usage/download/ :contentReference[oaicite:7]{index=7}
                    cmake = sh.Command("cmake")
                    shprint(
                        cmake,
                        "-DCMAKE_BUILD_TYPE=Release",
                        f"-DCMAKE_INSTALL_PREFIX={install_prefix}",
                        "..",
                        _env=env,
                    )
                    shprint(sh.make, "-j4", _env=env)
                    shprint(sh.make, "install", _env=env)


recipe = GeosRecipe()
