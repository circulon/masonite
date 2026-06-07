import importlib
import os
import sys
import tempfile
import textwrap
import unittest

from src.masonite.configuration import config

from tests import TestCase


class TestPackageProvider(TestCase):
    def test_config_is_merged(self):
        self.assertEqual(config("test_package.param_1"), "test")
        self.assertEqual(config("test_package.param_2"), 0)

    def test_views_are_registered(self):
        self.application.make("view").exists("test_package:package")
        self.application.make("view").exists("test_package:admin.settings")
        # this one has been published in project and overriden
        # check that the project view is used and not the package view
        self.assertEqual(
            self.application.make("view")
            .render("test_package:admin.settings")
            .rendered_template,
            "overriden",
        )

    def test_commands_are_registered(self):
        self.craft("test_package:command1").assertSuccess()
        self.craft("test_package:command2").assertSuccess()

    def test_routes_are_registered(self):
        self.get("/package/test/").assertContains("index")
        self.get("/api/package/test/").assertCreated()

    def test_presets_are_registered(self):
        output = self.craft("preset", "--list")
        # verify that the "test" preset has been registered
        output.assertOutputContains("test")
        # verify that the "test" preset can be ran
        self.craft("preset", "test").assertSuccess()


class TestPackageRootResolution(unittest.TestCase):
    """Regression tests for PackageProvider.root() — see issue #24."""

    def _build_package(self, base_dir, pkg_name):
        """Create a minimal installable package with a PackageProvider on disk
        and return the directory to put on sys.path."""
        site = os.path.join(base_dir, "site")
        pkg_dir = os.path.join(site, pkg_name)
        os.makedirs(os.path.join(pkg_dir, "providers"))
        os.makedirs(os.path.join(pkg_dir, "templates"))
        open(os.path.join(pkg_dir, "__init__.py"), "w").close()
        open(os.path.join(pkg_dir, "providers", "__init__.py"), "w").close()
        open(os.path.join(pkg_dir, "templates", "index.html"), "w").close()
        with open(os.path.join(pkg_dir, "providers", "Prov.py"), "w") as f:
            f.write(
                textwrap.dedent(
                    """
                    from src.masonite.packages import PackageProvider


                    class Prov(PackageProvider):
                        def configure(self):
                            self.root(__name__.split(".")[0])
                    """
                )
            )
        return site, pkg_dir

    def _load_provider(self, site, pkg_name):
        sys.path.insert(0, site)
        module = importlib.import_module(f"{pkg_name}.providers.Prov")
        return module.Prov(None)

    def _cleanup(self, site, pkg_name):
        sys.path = [p for p in sys.path if p != site]
        for name in list(sys.modules):
            if name == pkg_name or name.startswith(pkg_name + "."):
                del sys.modules[name]

    def test_root_resolves_when_project_path_contains_package_name(self):
        # The install path's parent ("<pkg>-smoke") contains the package name
        # *before* the real module directory. A substring search on __file__
        # would truncate abs_root to a nonexistent dir and crash on boot.
        pkg_name = "rootpkg"
        with tempfile.TemporaryDirectory(prefix=f"{pkg_name}-smoke-") as base_dir:
            site, pkg_dir = self._build_package(base_dir, pkg_name)
            try:
                provider = self._load_provider(site, pkg_name)
                provider.root(pkg_name)
                # abs_root must be the real package directory, and exist.
                self.assertEqual(provider.package.abs_root, pkg_dir)
                self.assertTrue(os.path.isdir(provider.package.abs_root))
                # views("templates") must then resolve to a real folder.
                self.assertTrue(
                    os.path.isdir(
                        os.path.join(provider.package.abs_root, "templates")
                    )
                )
            finally:
                self._cleanup(site, pkg_name)

    def test_root_resolves_module_root_and_abs_root(self):
        pkg_name = "plainpkg"
        with tempfile.TemporaryDirectory() as base_dir:
            site, pkg_dir = self._build_package(base_dir, pkg_name)
            try:
                provider = self._load_provider(site, pkg_name)
                provider.root(pkg_name)
                self.assertEqual(provider.package.module_root, pkg_name)
                self.assertEqual(provider.package.abs_root, pkg_dir)
            finally:
                self._cleanup(site, pkg_name)
