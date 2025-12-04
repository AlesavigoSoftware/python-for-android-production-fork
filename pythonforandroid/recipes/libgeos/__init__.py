from __future__ import annotations

import shutil
from multiprocessing import cpu_count
from os.path import exists, join

import sh
from pythonforandroid.recipe import Recipe
from pythonforandroid.toolchain import shprint
from pythonforandroid.util import current_directory, ensure_dir


class LibGeosRecipe(Recipe):
    """
    Рецепт GEOS для Android, заточенный под Shapely 2.x.

    Ключевые моменты:
    - Сборка только shared-библиотек (BUILD_SHARED_LIBS=ON)
    - После установки создаём версии .so, которые ожидают:
        * сам GEOS и его C-API (libgeos.so.<version>)
        * Shapely (libgeos_c.so.1)
    - В built_libraries регистрируем и versioned, и unversioned имена,
      чтобы Android-лоадер удовлетворил все зависимости.
    """

    name = "libgeos"
    # Версию можно обновлять, но тогда надо будет
    # заменить и в libgeos.so.<version> ниже.
    version = "3.12.2"

    # Старый, но рабочий алиас официального репозитория
    url = "https://github.com/libgeos/libgeos/archive/{version}.zip"

    depends: list[str] = []

    # Позволяем p4a тащить libc++_shared.so самостоятельно
    need_stl_shared = True

    # Этот словарь мы перезапишем в build_arch, но
    # базовое значение нужно, чтобы p4a не падал раньше времени.
    built_libraries = {
        "libgeos.so": "install_target/lib",
        "libgeos_c.so": "install_target/lib",
    }

    def build_arch(self, arch):
        source_dir = self.get_build_dir(arch.arch)
        build_target = join(source_dir, "build_target")
        install_target = join(source_dir, "install_target")

        ensure_dir(build_target)

        with current_directory(build_target):
            env = self.get_recipe_env(arch)

            # Конфигурация CMake под Android
            shprint(
                sh.cmake,
                source_dir,
                f"-DANDROID_ABI={arch.arch}",
                f"-DANDROID_NATIVE_API_LEVEL={self.ctx.ndk_api}",
                f"-DANDROID_STL={self.stl_lib_name}",
                "-DBUILD_SHARED_LIBS=ON",
                "-DGEOS_ENABLE_TESTS=OFF",
                "-DCMAKE_BUILD_TYPE=Release",
                "-DCMAKE_TOOLCHAIN_FILE={}".format(
                    join(
                        self.ctx.ndk_dir,
                        "build",
                        "cmake",
                        "android.toolchain.cmake",
                    )
                ),
                f"-DCMAKE_INSTALL_PREFIX={install_target}",
                _env=env,
            )

            # Сборка и установка
            shprint(sh.make, f"-j{cpu_count()}", _env=env)
            shprint(sh.make, "install", _env=env)

        # После установки нормализуем имена .so
        lib_dir = join(install_target, "lib")
        base_geos = join(lib_dir, "libgeos.so")
        base_geos_c = join(lib_dir, "libgeos_c.so")

        # 1) libgeos.so.<version> — чтобы удовлетворить зависимость
        #    libgeos_c.so → libgeos.so.3.12.2 (как в твоём логе)
        geos_versioned = join(lib_dir, f"libgeos.so.{self.version}")
        if exists(base_geos) and not exists(geos_versioned):
            shutil.copy2(base_geos, geos_versioned)

        # 2) libgeos_c.so.1 — чтобы Shapely мог сделать dlopen("libgeos_c.so.1")
        #    На реальных Linux/Alpine есть связка libgeos_c.so.1 → libgeos_c.so.1.x.y,
        #    но на Android symlink'и в apk/zip не гарантированы, поэтому делаем копию.
        geos_c_soname = join(lib_dir, "libgeos_c.so.1")
        if exists(base_geos_c) and not exists(geos_c_soname):
            shutil.copy2(base_geos_c, geos_c_soname)

        # Теперь регистрируем полный набор библиотек, которые p4a положит в APK.
        # Важно: и versioned, и unversioned имена.
        self.built_libraries = {
            "libgeos.so": "install_target/lib",
            f"libgeos.so.{self.version}": "install_target/lib",
            "libgeos_c.so": "install_target/lib",
            "libgeos_c.so.1": "install_target/lib",
        }

    # Небольшое API для ShapelyRecipe
    def get_geos_env(self, arch):
        """
        Возвращает переменные окружения, которые ожидает Shapely
        при сборке из исходников (см. раздел Installation / GEOS discovery).
        """
        source_dir = self.get_build_dir(arch.arch)
        install_target = join(source_dir, "install_target")
        include_dir = join(install_target, "include")
        lib_dir = join(install_target, "lib")

        return {
            # Куда класть -I
            "GEOS_INCLUDE_PATH": include_dir,
            # Для удобства дополнительно возвращаем lib-dir
            "GEOS_LIB_DIR": lib_dir,
            # В доках Shapely GEOS_LIBRARY_PATH — путь к каталогу lib
            "GEOS_LIBRARY_PATH": lib_dir,
        }


recipe = LibGeosRecipe()
