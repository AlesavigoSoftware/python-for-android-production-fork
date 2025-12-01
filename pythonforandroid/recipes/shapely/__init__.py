from os.path import join

from pythonforandroid.recipe import PyProjectRecipe, Recipe


class ShapelyRecipe(PyProjectRecipe):
    """
    Рецепт для Shapely 2.1.x.
    Собирает Shapely из исходников, используя уже установленный GEOS
    (путь к которому пробрасываем через GEOS_INCLUDE_PATH / GEOS_LIBRARY_PATH).
    """

    name = "shapely"
    version = "2.1.2"
    # Можно использовать либо GitHub, либо sdist с PyPI.
    # Вариант с GitHub:
    url = "https://github.com/shapely/shapely/archive/refs/tags/{version}.tar.gz"
    # либо:
    # url = "https://files.pythonhosted.org/packages/source/s/shapely/shapely-{version}.tar.gz"

    # Нам нужен установленный geos до сборки shapely
    depends = ["python3", "geos"]

    # Имя пакета в site-packages
    site_packages_name = "shapely"

    def get_recipe_env(self, arch):
        # базовое окружение от PyProjectRecipe
        env = super().get_recipe_env(arch)

        # Получаем рецепт geos и его env с путями
        geos_recipe = Recipe.get_recipe("geos", self.ctx)
        geos_env = geos_recipe.get_geos_env(arch)

        # Официальный гайд Shapely: можно указывать пути к GEOS через
        # переменные GEOS_INCLUDE_PATH и GEOS_LIBRARY_PATH. :contentReference[oaicite:11]{index=11}
        env.update(geos_env)

        # Если очень хочется, можно дополнительно подсунуть geos-config,
        # но в минимальном варианте достаточно этих переменных.
        return env

    # build_arch можно не перегружать: PyProjectRecipe сам вызовет
    # сборку/установку через pyproject/pep517, используя env с GEOS_*.


recipe = ShapelyRecipe()
