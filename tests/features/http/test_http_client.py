import unittest
from unittest.mock import patch, MagicMock

import requests

from tests import TestCase
from src.masonite.http import HTTPClient, HTTPResponse


class TestHTTPClient(unittest.TestCase):
    def setUp(self):
        self.http = HTTPClient()

    def test_fake_returns_stubbed_response(self):
        self.http.fake(
            {"example.test/users": HTTPClient.response({"id": 1}, status=201)}
        )
        response = self.http.get("https://example.test/users")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), {"id": 1})
        self.assertTrue(response.ok())
        self.assertTrue(response.successful())

    def test_wildcard_stub_is_fallback(self):
        self.http.fake({"*": HTTPClient.response("pong")})
        self.assertEqual(self.http.get("https://anything.test").text(), "pong")

    def test_with_token_and_headers_are_sent(self):
        self.http.fake({"*": HTTPClient.response("ok")})
        self.http.with_token("secret").with_headers({"X-Trace": "abc"}).post(
            "https://example.test", json={"a": 1}
        )
        sent = self.http.recorded()[0]
        self.assertEqual(sent["headers"]["Authorization"], "Bearer secret")
        self.assertEqual(sent["headers"]["X-Trace"], "abc")
        self.assertEqual(sent["json"], {"a": 1})

    def test_assertions_about_sent_requests(self):
        self.http.fake({"*": HTTPClient.response("ok")})
        self.http.get("https://example.test/a")
        self.http.get("https://example.test/b")
        self.http.assert_sent("example.test/a")
        self.http.assert_sent_count(2)

    def test_assert_nothing_sent(self):
        self.http.fake()
        self.http.assert_nothing_sent()

    def test_response_status_helpers(self):
        self.assertTrue(HTTPResponse(404).client_error())
        self.assertTrue(HTTPResponse(503).server_error())
        self.assertTrue(HTTPResponse(500).failed())
        self.assertEqual(HTTPResponse(200, {"a": 1}).json(), {"a": 1})

    def test_retry_recovers_after_transient_errors(self):
        attempts = {"count": 0}

        def side_effect(*args, **kwargs):
            attempts["count"] += 1
            if attempts["count"] < 3:
                raise requests.ConnectionError("boom")
            response = MagicMock()
            response.status_code = 200
            response.content = b'{"ok": true}'
            response.headers = {}
            return response

        with patch("requests.request", side_effect=side_effect):
            response = self.http.retry(3, sleep=0).get("https://example.test")

        self.assertEqual(attempts["count"], 3)
        self.assertEqual(response.json(), {"ok": True})

    def test_retry_reraises_when_exhausted(self):
        with patch("requests.request", side_effect=requests.ConnectionError("boom")):
            with self.assertRaises(requests.ConnectionError):
                self.http.retry(2, sleep=0).get("https://example.test")


class TestHTTPClientBinding(TestCase):
    def test_http_is_bound_in_the_container(self):
        self.assertIsInstance(self.application.make("http"), HTTPClient)
