from pythonforandroid.recipe import PyProjectRecipe, Recipe


class PyprojRecipe(PyProjectRecipe):
    """
    Сборка pyproj из исходников, с линковкой на собранный выше PROJ.
    """

    name = "pyproj"
    version = "3.7.2"
    url = "https://github.com/pyproj4/pyproj/archive/refs/tags/{version}.tar.gz"

    # python3 добавится автоматически, но можно указать явно
    depends = ["python3", "proj"]

    # имя в site-packages (по умолчанию совпадает с name, но можно задать явно)
    site_packages_name = "pyproj"

    def get_recipe_env(self, arch, **kwargs):
        # базовое окружение (include/lib для Android)
        env = super().get_recipe_env(arch)

        # подтягиваем рецепт PROJ и его пути
        proj_recipe = Recipe.get_recipe("proj", self.ctx)
        proj_env = proj_recipe.get_proj_env(arch)

        # pyproj при сборке читает эти переменные (PROJ_DIR / PROJ_LIBDIR / PROJ_INCDIR)
        env.update(proj_env)
        return env


recipe = PyprojRecipe()
