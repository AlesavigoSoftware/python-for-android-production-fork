from __future__ import annotations

from pythonforandroid.recipe import PyProjectRecipe, Recipe


class ShapelyRecipe(PyProjectRecipe):
    """
    Рецепт Shapely 2.x для Android.

    - Собирается из sdist (PyProjectRecipe + pyproject.toml)
    - Линкуется с GEOS, который собирает libgeos/LibGeosRecipe
    - Среда для сборки настраивается через get_recipe_env:
        * CFLAGS: добавляем -I<GEOS_INCLUDE_PATH>
        * LDFLAGS: добавляем -L<GEOS_LIB_DIR> -lgeos_c -lgeos
    """

    name = "shapely"
    version = "2.1.2"
    url = "https://github.com/shapely/shapely/archive/refs/tags/{version}.tar.gz"

    depends = ["libgeos"]

    site_packages_name = "shapely"

    # Позволяем p4a самому подтянуть libc++_shared.so
    need_stl_shared = True

    def get_recipe_env(self, arch, **kwargs):
        env = super().get_recipe_env(arch, **kwargs)

        # Получаем инфу от рецепта geos
        geos_recipe = Recipe.get_recipe("libgeos", self.ctx)
        geos_env = geos_recipe.get_geos_env(arch)
        env.update(geos_env)

        geos_inc = geos_env["GEOS_INCLUDE_PATH"]
        geos_lib_dir = geos_env["GEOS_LIB_DIR"]

        # ---- CFLAGS: добавляем include-директорию GEOS ---------------------
        cflags = env.get("CFLAGS", "")
        if f"-I{geos_inc}" not in cflags:
            cflags = (cflags + f" -I{geos_inc}").strip()
        env["CFLAGS"] = cflags

        # ---- LDFLAGS: добавляем lib-директорию + линковку с geos/geos_c ----
        ldflags = env.get("LDFLAGS", "")
        if f"-L{geos_lib_dir}" not in ldflags:
            ldflags = (ldflags + f" -L{geos_lib_dir}").strip()

        # аккуратно добавляем -lgeos_c и -lgeos
        for flag in ("-lgeos_c", "-lgeos"):
            if flag not in ldflags:
                ldflags += f" {flag}"
        env["LDFLAGS"] = ldflags.strip()

        # На всякий случай оставляем GEOS_LIBRARY_PATH — Shapely умеет его читать
        # (по докам это каталог с lib, а не конкретный .so)
        env["GEOS_LIBRARY_PATH"] = geos_env["GEOS_LIBRARY_PATH"]

        # !!! Специально НЕ добавляем сюда -lc++_shared: этим занимается p4a.
        return env


recipe = ShapelyRecipe()
