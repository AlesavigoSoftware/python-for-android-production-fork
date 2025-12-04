from __future__ import annotations

import os
from os.path import join, exists

import sh
from multiprocessing import cpu_count

from pythonforandroid.recipe import Recipe
from pythonforandroid.toolchain import current_directory, shprint
from pythonforandroid.logger import info


class ProjRecipe(Recipe):
    """
    Рецепт для сборки библиотеки PROJ (https://proj.org) под Android.

    Особенности:
    - Используем CMake.
    - PROJ >= 6 требует SQLite3 как обязательную зависимость (proj.db).
    - Берём SQLite3 из p4a-рецепта `sqlite3` и явно передаём пути
      в CMake через SQLite3_INCLUDE_DIR и SQLite3_LIBRARY.
    - Отключаем утилиту `projsync` (BUILD_PROJSYNC=OFF), чтобы не
      тащить Curl и не ловить ошибку "projsync requires Curl".
    - Предоставляем pyproj окружение через get_proj_env():
      PROJ_DIR / PROJ_LIBDIR / PROJ_INCDIR / PROJ_VERSION.
    """

    name = "proj"
    version = "9.4.0"
    url = "https://download.osgeo.org/proj/proj-{version}.tar.gz"

    # PROJ зависит от sqlite3 (proj.db на SQLite)
    depends = ["sqlite3"]

    # Используем статическую libproj.a из install/lib
    built_libraries = {"libproj.a": "install/lib"}

    def build_arch(self, arch):
        """
        Сборка PROJ для конкретной архитектуры (armeabi-v7a, arm64-v8a и т.п.).
        """
        build_dir = self.get_build_dir(arch.arch)
        install_dir = join(build_dir, "install")

        info(f"[proj] build_dir = {build_dir}")
        info(f"[proj] install_dir = {install_dir}")

        # --- Поднимаем пути к SQLite3 из рецепта sqlite3 -------------------
        sqlite3_recipe = Recipe.get_recipe("sqlite3", self.ctx)
        sqlite_build_dir = sqlite3_recipe.get_build_dir(arch.arch)

        # В логах sqlite3 видно:
        #   Install : libsqlite3.so => libs/<arch>/libsqlite3.so
        sqlite_include_dir = sqlite_build_dir  # здесь лежит sqlite3.c/sqlite3.h
        sqlite_lib_path = join(sqlite_build_dir, "libs", arch.arch, "libsqlite3.so")

        if not exists(sqlite_lib_path):
            raise RuntimeError(
                "[proj] Не удалось найти libsqlite3.so по пути: {}\n"
                "Ожидалось, что рецепт sqlite3 соберёт библиотеку в "
                "'<sqlite_build_dir>/libs/<arch>/libsqlite3.so'.".format(
                    sqlite_lib_path
                )
            )

        info(f"[proj] using SQLite3_INCLUDE_DIR = {sqlite_include_dir}")
        info(f"[proj] using SQLite3_LIBRARY      = {sqlite_lib_path}")

        # --- Окружение p4a (NDK-компиляторы, флаги и т.п.) ------------------
        env = self.get_recipe_env(arch)

        # Host-side sqlite3 CLI, используется CMake-скриптами PROJ
        # для генерации/миграции proj.db на машине сборки, а не на устройстве.
        env.setdefault("EXE_SQLITE3", "sqlite3")

        # Удаляем autoconf proj_config.h, чтобы он не мешал CMake
        autoconf_proj_config = join(build_dir, "src", "proj_config.h")
        if exists(autoconf_proj_config):
            info(f"[proj] Removing autoconf proj_config.h: {autoconf_proj_config}")
            try:
                os.remove(autoconf_proj_config)
            except OSError:
                info("[proj] Failed to remove autoconf proj_config.h, продолжаем")

        # --- Запуск CMake из каталога с CMakeLists.txt ----------------------
        with current_directory(build_dir):
            # Если CMakeLists.txt в корне — используем его,
            # иначе ищем подкаталог proj-<version>.
            src_dir = "."
            if not exists("CMakeLists.txt"):
                candidate = f"proj-{self.version}"
                if exists(join(candidate, "CMakeLists.txt")):
                    src_dir = candidate
                else:
                    raise RuntimeError(
                        "[proj] Не найден CMakeLists.txt ни в {}, ни в {}".format(
                            build_dir, candidate
                        )
                    )

            with current_directory(src_dir):
                cmake_args = [
                    "-DCMAKE_BUILD_TYPE=Release",
                    f"-DCMAKE_INSTALL_PREFIX={install_dir}",
                    # Статическая сборка libproj.a
                    "-DBUILD_SHARED_LIBS=OFF",
                    # Отключаем тесты и необязательные зависимости
                    "-DBUILD_TESTING=OFF",
                    "-DENABLE_CURL=OFF",
                    "-DENABLE_TIFF=OFF",
                    # Ключ: выключить projsync, чтобы не требовался Curl
                    "-DBUILD_PROJSYNC=OFF",
                    # Явно говорим CMake, где искать SQLite3
                    f"-DSQLite3_INCLUDE_DIR={sqlite_include_dir}",
                    f"-DSQLite3_LIBRARY={sqlite_lib_path}",
                    # На всякий случай дублируем старые имена
                    f"-DSQLITE3_INCLUDE_DIR={sqlite_include_dir}",
                    f"-DSQLITE3_LIBRARY={sqlite_lib_path}",
                    ".",
                ]

                info("[proj] Running CMake with args:")
                for a in cmake_args:
                    info("    " + a)

                # Конфигурация
                shprint(sh.cmake, *cmake_args, _env=env)

                # Сборка и установка
                shprint(
                    sh.cmake,
                    "--build",
                    ".",
                    "--target",
                    "install",
                    "-j",
                    str(cpu_count()),
                    _env=env,
                )

    # --- Хук для pyproj-рецепта ---------------------------------------------

    def get_proj_env(self, arch):
        """
        Возвращает env-переменные для сборки pyproj и других зависимых рецептов.

        pyproj при кросс-компиляции:
        - ищет пути к PROJ через PROJ_DIR/PROJ_LIBDIR/PROJ_INCDIR;
        - при наличии PROJ_VERSION НЕ пытается запускать бинарник proj
          из PROJ_DIR/bin/proj, а использует версию из переменной.
        """
        build_dir = self.get_build_dir(arch.arch)
        install_dir = join(build_dir, "install")
        inc_dir = join(install_dir, "include")
        lib_dir = join(install_dir, "lib")

        env = {
            "PROJ_DIR": install_dir,
            "PROJ_LIBDIR": lib_dir,
            "PROJ_INCDIR": inc_dir,
            "PROJ_VERSION": self.version,
        }

        info("[proj] get_proj_env ->")
        for k, v in env.items():
            info(f"    {k} = {v}")

        return env


recipe = ProjRecipe()
