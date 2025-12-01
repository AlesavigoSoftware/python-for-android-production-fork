from pythonforandroid.recipe import Recipe
from pythonforandroid.toolchain import current_directory, shprint
from os.path import join
import sh


class ProjRecipe(Recipe):
    """
    Сборка C-библиотеки PROJ в локный префикс внутри build_dir.
    """

    name = "proj"
    version = "9.4.0"
    url = "https://download.osgeo.org/proj/proj-{version}.tar.gz"

    # если нужно — пропиши зависимости на zlib/tiff/curl и т.п.
    # depends = ["python3", "zlib", "libtiff", "libcurl"]

    def get_install_prefix(self, arch):
        # сюда будем делать `make install`
        return join(self.get_build_dir(arch.arch), "install")

    def build_arch(self, arch):
        super().build_arch(arch)
        env = self.get_recipe_env(arch)  # CC, CFLAGS, LDFLAGS под Android
        build_dir = self.get_build_dir(arch.arch)
        install_prefix = self.get_install_prefix(arch)

        src_dir = f"proj-{self.version}"

        with current_directory(build_dir):
            # исходники p4a уже распакует сам (по url), думаем только о сборке
            with current_directory(src_dir):
                # configure: флаг --host можно не трогать, p4a уже подставил нужный CC/AR/LD
                shprint(
                    sh.Command("./configure"),
                    f"--prefix={install_prefix}",
                    "--disable-shared",
                    "--enable-static",
                    _env=env,
                )
                shprint(sh.make, "-j4", _env=env)
                shprint(sh.make, "install", _env=env)

    # helper, чтобы pyproj мог легко забрать пути
    def get_proj_env(self, arch):
        root = self.get_install_prefix(arch)
        return {
            "PROJ_DIR": root,
            "PROJ_LIBDIR": join(root, "lib"),
            "PROJ_INCDIR": join(root, "include"),
        }


recipe = ProjRecipe()
