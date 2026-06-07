import os
import importlib.util
from collections import defaultdict
from os.path import relpath, join, basename, isdir, isfile, dirname
import shutil

from ...providers.Provider import Provider
from ...exceptions import InvalidPackageName
from ...utils.location import (
    base_path,
    config_path,
    views_path,
    migrations_path,
    resources_path,
)
from ...facades import Config
from ...utils.time import migration_timestamp
from ...routes import Route
from ...utils.structures import load
from ...utils.str import modularize, as_filepath
from ...utils.filesystem import make_directory

from ..reserved_names import PACKAGE_RESERVED_NAMES
from ..Package import Package


class PackageProvider(Provider):

    vendor_prefix = "vendor"

    def __init__(self, application):
        self.application = application
        # TODO: the default here could be set auto by deciding that its the dirname
        # containing the provider !
        self.package = Package()
        self.default_resources = ["config", "views", "migrations", "assets"]

    def register(self):
        self.configure()

    def boot(self):
        pass

    # api
    def configure(self):
        pass

    def publish(self, resources, dry=False):
        project_root = base_path()
        resources_list = resources or self.default_resources
        published_resources = defaultdict(lambda: [])
        for resource in resources_list:
            resource = self.package.resources.get(resource)
            if not resource:
                continue
            for source, dest in resource.files:
                if not dry:
                    make_directory(dest)
                    shutil.copy(source, dest)
                published_resources[resource.key].append(relpath(dest, project_root))
        return published_resources

    def root(self, relative_dir):
        """Define python package module root path and absolute package root path.
        It works when installing the package locally with: pip install . or pip install -e .
        and when installing the package from production release with: pip install package-name
        """
        # get relative module path to package root
        relative_module_path = modularize(relative_dir)
        self.package.module_root = self.__module__[
            0 : self.__module__.find(relative_module_path) + len(relative_module_path)
        ]
        # Resolve the package's absolute directory through the import system
        # rather than a first-occurrence substring match on the provider's
        # __file__. A substring search breaks when the *project* path itself
        # contains the package name before the real module directory — e.g. an
        # app created at /tmp/collapsar-smoke, or an editable install from a
        # repo dir named like the package — because find() matches too early
        # and points abs_root at a truncated, nonexistent directory. See #24.
        self.package.abs_root = self._resolve_package_root(self.package.module_root)
        return self

    def _resolve_package_root(self, module_root):
        """Return the absolute directory of an importable package.

        Uses ``importlib`` so the lookup is immune to a project path that
        happens to contain the package name. Falls back to the legacy
        substring resolution only if the import system has no spec for the
        package (exotic loaders).
        """
        spec = importlib.util.find_spec(module_root)
        if spec is not None and spec.submodule_search_locations:
            return list(spec.submodule_search_locations)[0]
        if spec is not None and spec.origin:
            return dirname(spec.origin)
        # Legacy fallback: derive the root from the provider file path.
        module_root_path = as_filepath(module_root)
        provider_file = load(self.__module__).__file__
        return provider_file[
            0 : provider_file.find(module_root_path) + len(module_root_path)
        ]

    def name(self, name):
        if name in PACKAGE_RESERVED_NAMES:
            raise InvalidPackageName(
                f"{name} is a reserved name. Please choose another name for your package."
            )
        self.package.name = name
        return self

    def vendor_name(self, name):
        self.package.vendor_name = name
        return self

    def config(self, config_filepath, publish=False):
        # TODO: a name must be specified !
        self.package.add_config(config_filepath)
        Config.merge_with(self.package.name, self.package.config)
        if publish:
            self.package.add_publishable_resource(
                "config", config_filepath, config_path(f"{self.package.name}.py")
            )
        return self

    def views(self, location, publish=False):
        """Register views location in the project. location must be a folder containinng the views you want to publish."""
        self.package.add_views(location)
        # register views into project
        self.application.make("view").add_namespaced_location(
            self.package.name, self.package.views
        )

        if publish:
            location_abs_path = self.package._build_path(location)
            for dirpath, _, filenames in os.walk(location_abs_path):
                for f in filenames:
                    # don't add other files than templates
                    view_abs_path = join(dirpath, f)
                    _, ext = os.path.splitext(view_abs_path)
                    if ext != ".html":
                        continue
                    self.package.add_publishable_resource(
                        "views",
                        view_abs_path,
                        views_path(
                            join(
                                self.vendor_prefix,
                                self.package.name,
                                relpath(view_abs_path, location_abs_path),
                            )
                        ),
                    )

        return self

    def commands(self, *commands):
        self.application.make("commands").add(*commands)
        return self

    def presets(self, *presets):
        for preset in presets:
            self.application.make("presets").add(preset)
        return self

    def migrations(self, *migrations):
        self.package.add_migrations(*migrations)
        # use same timestamp for all package migrations
        timestamp = migration_timestamp()
        for index, migration in enumerate(migrations):
            self.package.add_publishable_resource(
                "migrations",
                migration,
                migrations_path(f"{timestamp}{index + 1}_{basename(migration)}"),
            )
        return self

    def routes(self, *routes):
        """Controller locations must have been loaded already !"""
        self.package.add_routes(*routes)
        for route_group in self.package.routes:
            self.application.make("router").add(
                Route.group(load(route_group, "ROUTES", []), middleware=["web"])
            )
        return self

    def controllers(self, *controller_locations):
        self.package.add_controller_locations(*controller_locations)
        Route.add_controller_locations(*self.package.controller_locations)
        return self

    def assets(self, *assets):
        self.package.add_assets(*assets)
        for asset_dir_or_file in assets:
            abs_path = self.package._build_path(asset_dir_or_file)
            if isdir(abs_path):
                for dirpath, _, filenames in os.walk(abs_path):
                    for f in filenames:
                        asset_abs_path = join(dirpath, f)
                        self.package.add_publishable_resource(
                            "assets",
                            asset_abs_path,
                            resources_path(
                                join(
                                    self.vendor_prefix,
                                    self.package.name,
                                    relpath(asset_abs_path, abs_path),
                                )
                            ),
                        )
            elif isfile(abs_path):
                self.package.add_publishable_resource(
                    "assets",
                    abs_path,
                    resources_path(
                        join(
                            self.vendor_prefix,
                            self.package.name,
                            asset_dir_or_file,
                        )
                    ),
                )

        return self
