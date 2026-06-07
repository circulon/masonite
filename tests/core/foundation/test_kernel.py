import os
import subprocess
import sys
import unittest

from src.masonite.foundation import Application, CoreKernel, Kernel


def fresh_app():
    """Build an Application with an isolated container.

    ``Container.objects`` is a class-level dict shared across every
    ``Application`` instance, so kernel tests would otherwise see bindings
    leaked from other tests (e.g. the ``wsgi`` singleton booted by the
    framework ``TestCase``). Shadowing it with a fresh per-instance dict
    gives each test a clean container.
    """
    app = Application(os.getcwd())
    app.objects = {}
    return app


class TestCoreKernel(unittest.TestCase):
    def test_registers_framework_machinery(self):
        app = fresh_app()
        CoreKernel(app).register()

        self.assertTrue(app.has("middleware"))
        self.assertTrue(app.has("router"))
        self.assertTrue(app.has("loader"))
        self.assertTrue(app.has("commands"))
        self.assertEqual(
            app.get_storage_path(), os.path.join(app.base_path, "storage")
        )
        self.assertIsNotNone(app.get_response_handler())

    def test_command_registry_is_empty(self):
        app = fresh_app()
        CoreKernel(app).register()

        # The bare-metal kernel binds the registry but registers no commands.
        self.assertEqual(app.make("commands").command_name, [])

    def test_does_not_register_testing(self):
        app = fresh_app()
        CoreKernel(app).register()

        self.assertFalse(app.has("tests.response"))

    def test_make_commands_returns_the_same_capsule(self):
        app = fresh_app()
        CoreKernel(app).register()

        # register_commands() relies on make() returning the bound instance so
        # that .add() mutates the registry in place (providers append to it
        # later during boot()).
        self.assertIs(app.make("commands"), app.make("commands"))


class TestKernel(unittest.TestCase):
    def test_kernel_extends_core_kernel(self):
        self.assertTrue(issubclass(Kernel, CoreKernel))

    def test_registers_built_in_commands(self):
        app = fresh_app()
        Kernel(app).register()

        names = app.make("commands").command_name
        for expected in ("serve", "key", "tinker", "down", "up"):
            self.assertIn(expected, names)
        self.assertGreaterEqual(len(names), 21)

    def test_registers_testing_under_test_runner(self):
        # The suite runs under pytest, so is_running_tests() is True and the
        # framework kernel wires up the test response capsule for every app.
        app = fresh_app()
        Kernel(app).register()

        self.assertTrue(app.has("tests.response"))

    def test_register_runs_in_order_without_error(self):
        # super().register() must run before register_commands() so the
        # "commands" binding exists when make("commands") is called.
        app = fresh_app()
        Kernel(app).register()  # must not raise

        self.assertTrue(app.has("commands"))


class TestKernelLazyImports(unittest.TestCase):
    def test_importing_foundation_stays_light(self):
        # Importing the foundation package (and the kernels) must not pull in
        # cleo, the command suite, or the testing helpers. Asserted in a fresh
        # interpreter because pytest/cleo are already loaded in this process.
        code = (
            "import sys\n"
            "import src.masonite.foundation\n"
            "from src.masonite.foundation import Kernel, CoreKernel, Application\n"
            "mods = list(sys.modules)\n"
            "assert not any(m == 'cleo' or m.startswith('cleo.') for m in mods), 'cleo imported'\n"
            "assert not any(m.endswith('masonite.commands') for m in mods), 'commands imported'\n"
            "assert not any('masonite.tests' in m for m in mods), 'tests imported'\n"
            "print('OK')\n"
        )
        result = subprocess.run(
            [sys.executable, "-c", code],
            cwd=os.getcwd(),
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("OK", result.stdout)


if __name__ == "__main__":
    unittest.main()
