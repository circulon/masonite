import unittest

from src.masonite.commands.ServeCommand import ServeCommand


class StubConfig:
    """Minimal config double with the get/set surface ServeCommand uses."""

    def __init__(self, values):
        self._values = dict(values)

    def get(self, path, default=None):
        return self._values.get(path, default)

    def set(self, path, value):
        self._values[path] = value


class StubApp:
    def __init__(self, config):
        self._config = config

    def make(self, name):
        assert name == "config"
        return self._config


class TestServeCommandAppUrl(unittest.TestCase):
    def sync(self, app_url, host, port):
        values = {} if app_url is None else {"application.app_url": app_url}
        config = StubConfig(values)
        ServeCommand(StubApp(config))._sync_app_url(host, port)
        return config.get("application.app_url")

    def test_rewrites_host_and_port(self):
        self.assertEqual(
            self.sync("http://localhost:8000/", "0.0.0.0", "9000"),
            "http://0.0.0.0:9000/",
        )

    def test_adds_port_when_missing(self):
        self.assertEqual(
            self.sync("http://localhost/", "127.0.0.1", "8080"),
            "http://127.0.0.1:8080/",
        )

    def test_preserves_scheme_and_path(self):
        self.assertEqual(
            self.sync("https://example.com:443/app", "0.0.0.0", "9000"),
            "https://0.0.0.0:9000/app",
        )

    def test_preserves_credentials(self):
        self.assertEqual(
            self.sync("http://user:pass@localhost:8000/", "0.0.0.0", "9000"),
            "http://user:pass@0.0.0.0:9000/",
        )

    def test_leaves_unset_url_untouched(self):
        self.assertIsNone(self.sync(None, "0.0.0.0", "9000"))

    def test_leaves_schemeless_url_untouched(self):
        self.assertEqual(self.sync("localhost", "0.0.0.0", "9000"), "localhost")
