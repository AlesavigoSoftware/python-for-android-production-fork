from __future__ import annotations

import glob
import os
import shutil
from os.path import join, exists

from pythonforandroid.recipe import PyProjectRecipe, Recipe


class PyprojRecipe(PyProjectRecipe):
    name = "pyproj"
    version = "3.5.0"
    url = "https://github.com/pyproj4/pyproj/archive/refs/tags/{version}.tar.gz"
    depends = ["proj"]

    site_packages_name = "pyproj"

    def get_recipe_env(self, arch, **kwargs):
        env = super().get_recipe_env(arch, **kwargs)

        proj_recipe = Recipe.get_recipe("proj", self.ctx)
        env.update(proj_recipe.get_proj_env(arch))

        libs_dir = self.ctx.get_libs_dir(arch.arch)

        ldflags = env.get("LDFLAGS", "")
        if f"-L{libs_dir}" not in ldflags:
            ldflags += f" -L{libs_dir}"
        if "-lc++_shared" not in ldflags:
            ldflags += " -lc++_shared"
        env["LDFLAGS"] = ldflags.strip()

        cxxflags = env.get("CXXFLAGS", "")
        if "-std=c++17" not in cxxflags:
            cxxflags += " -std=c++17"
        env["CXXFLAGS"] = cxxflags.strip()

        return env

    def postbuild_arch(self, arch):
        # 1. стандартная установка wheel
        super().postbuild_arch(arch)

        # 2. путь до pyproj в site-packages
        site_packages = self.ctx.get_site_packages_dir(arch)
        pyproj_dir = join(site_packages, "pyproj")

        # 3. копируем proj.db и прочие файлы в pyproj/proj_data
        proj_recipe = Recipe.get_recipe("proj", self.ctx)
        proj_build_dir = proj_recipe.get_build_dir(arch.arch)
        proj_data_dir = join(proj_build_dir, "install", "share", "proj")

        if exists(proj_data_dir):
            target_dir = join(pyproj_dir, "proj_data")
            if exists(target_dir):
                shutil.rmtree(target_dir)
            shutil.copytree(proj_data_dir, target_dir)
            print(f"[pyproj] copied PROJ data to {target_dir}")
        else:
            print(f"[pyproj] WARNING: proj data dir not found: {proj_data_dir}")

        # 4. патчим __init__.py, чтобы ИНИЦИАЛИЗАЦИЯ шла до _pyproj_global_context_initialize
        init_py = join(pyproj_dir, "__init__.py")
        if not exists(init_py):
            return

        with open(init_py, "r", encoding="utf-8") as fp:
            init_src = fp.read()

        marker = "# Android integration: configure PROJ data dir automatically"

        # убираем все старые наши блоки (если уже были добавлены ранее)
        if marker in init_src:
            init_src = init_src.split(marker, 1)[0].rstrip() + "\n"

        # код, который нужно вставить (один раз)
        android_snippet = (
            "\n"
            "# Android integration: configure PROJ data dir automatically\n"
            "try:\n"
            "    from . import datadir as _af_datadir\n"
            "    import os as _af_os\n"
            "    from pathlib import Path as _af_Path\n"
            "    _af_pkg = _af_Path(__file__).resolve().parent\n"
            "    _af_data = _af_pkg / 'proj_data'\n"
            "    if _af_data.is_dir():\n"
            "        _af_datadir.set_data_dir(str(_af_data))\n"
            "        _af_os.environ.setdefault('PROJ_DATA', str(_af_data))\n"
            "        _af_os.environ.setdefault('PROJ_LIB', str(_af_data))\n"
            "        print('[pyproj] Android PROJ data bootstrap:', _af_data)\n"
            "except Exception as _af_exc:\n"
            "    print('[pyproj] Android PROJ data bootstrap failed:', repr(_af_exc))\n"
            "\n"
        )

        # точка вставки — ПЕРЕД первым try: _pyproj_global_context_initialize()
        needle = "try:\n    _pyproj_global_context_initialize()"
        idx = init_src.find(needle)

        if idx != -1:
            new_src = init_src[:idx] + android_snippet + init_src[idx:]
        else:
            # на всякий случай, если сигнатура изменилась — просто допишем в конец
            new_src = init_src.rstrip() + android_snippet

        with open(init_py, "w", encoding="utf-8") as fp:
            fp.write(new_src)

        # 5. чистим байткод, чтобы точно использовалась новая версия
        init_pyc_direct = join(pyproj_dir, "__init__.pyc")
        if exists(init_pyc_direct):
            try:
                os.remove(init_pyc_direct)
                print("[pyproj] removed stale __init__.pyc")
            except OSError:
                pass

        cache_dir = join(pyproj_dir, "__pycache__")
        if exists(cache_dir):
            for fname in glob.glob(join(cache_dir, "__init__*.pyc")):
                try:
                    os.remove(fname)
                    print(f"[pyproj] removed stale {fname}")
                except OSError:
                    pass


recipe = PyprojRecipe()
