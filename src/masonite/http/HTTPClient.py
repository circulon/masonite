import time

import requests

from .HTTPResponse import HTTPResponse


class PendingRequest:
    """A fluent, single-use builder that configures and sends one request."""

    def __init__(self, client: "HTTPClient"):
        self._client = client
        self._headers = {}
        self._auth = None
        self._timeout = 30
        self._retries = 0
        self._retry_sleep = 0

    def with_headers(self, headers: dict) -> "PendingRequest":
        self._headers.update(headers)
        return self

    def with_token(self, token: str, prefix: str = "Bearer") -> "PendingRequest":
        self._headers["Authorization"] = f"{prefix} {token}"
        return self

    def with_basic_auth(self, username: str, password: str) -> "PendingRequest":
        self._auth = (username, password)
        return self

    def timeout(self, seconds: int) -> "PendingRequest":
        self._timeout = seconds
        return self

    def retry(self, times: int, sleep: int = 0) -> "PendingRequest":
        self._retries = times
        self._retry_sleep = sleep
        return self

    def get(self, url: str, query: dict = None) -> HTTPResponse:
        return self.send("GET", url, params=query)

    def post(self, url: str, data: dict = None, json: dict = None) -> HTTPResponse:
        return self.send("POST", url, data=data, json=json)

    def put(self, url: str, data: dict = None, json: dict = None) -> HTTPResponse:
        return self.send("PUT", url, data=data, json=json)

    def patch(self, url: str, data: dict = None, json: dict = None) -> HTTPResponse:
        return self.send("PATCH", url, data=data, json=json)

    def delete(self, url: str, data: dict = None, json: dict = None) -> HTTPResponse:
        return self.send("DELETE", url, data=data, json=json)

    def send(
        self, method: str, url: str, params=None, data=None, json=None
    ) -> HTTPResponse:
        if self._client.is_faking():
            self._client._record(
                {
                    "method": method,
                    "url": url,
                    "params": params,
                    "data": data,
                    "json": json,
                    "headers": dict(self._headers),
                }
            )
            return self._client._stub_for(url)

        last_exception = None
        for attempt in range(self._retries + 1):
            try:
                response = requests.request(
                    method,
                    url,
                    headers=self._headers or None,
                    params=params,
                    data=data,
                    json=json,
                    auth=self._auth,
                    timeout=self._timeout,
                )
                return HTTPResponse.from_requests(response)
            except requests.RequestException as exception:
                last_exception = exception
                if attempt < self._retries:
                    if self._retry_sleep:
                        time.sleep(self._retry_sleep)
                    continue
                raise last_exception


class HTTPClient:
    """Fluent HTTP client, resolved from the container as ``http`` and exposed
    through the ``Http`` facade.

    ```python
    from masonite.facades import Http

    response = Http.with_token("secret").get("https://example.test/api/users")
    response.json()
    ```

    In tests, call ``Http.fake({...})`` to stub outbound calls and record what
    was sent.
    """

    def __init__(self):
        self._faking = False
        self._stubs = {}
        self._recorded = []

    # -- Fluent entry points (each starts a fresh PendingRequest) ----------
    def with_headers(self, headers: dict) -> PendingRequest:
        return self._pending().with_headers(headers)

    def with_token(self, token: str, prefix: str = "Bearer") -> PendingRequest:
        return self._pending().with_token(token, prefix)

    def with_basic_auth(self, username: str, password: str) -> PendingRequest:
        return self._pending().with_basic_auth(username, password)

    def timeout(self, seconds: int) -> PendingRequest:
        return self._pending().timeout(seconds)

    def retry(self, times: int, sleep: int = 0) -> PendingRequest:
        return self._pending().retry(times, sleep)

    def get(self, url: str, query: dict = None) -> HTTPResponse:
        return self._pending().get(url, query)

    def post(self, url: str, data: dict = None, json: dict = None) -> HTTPResponse:
        return self._pending().post(url, data, json)

    def put(self, url: str, data: dict = None, json: dict = None) -> HTTPResponse:
        return self._pending().put(url, data, json)

    def patch(self, url: str, data: dict = None, json: dict = None) -> HTTPResponse:
        return self._pending().patch(url, data, json)

    def delete(self, url: str, data: dict = None, json: dict = None) -> HTTPResponse:
        return self._pending().delete(url, data, json)

    def _pending(self) -> PendingRequest:
        return PendingRequest(self)

    # -- Testing helpers ---------------------------------------------------
    @staticmethod
    def response(body=b"", status: int = 200, headers: dict = None) -> HTTPResponse:
        """Build a fake response to register as a stub."""
        return HTTPResponse(status, body, headers)

    def fake(self, stubs: dict = None) -> "HTTPClient":
        """Stop real requests from going out. ``stubs`` maps a URL substring (or
        ``"*"``) to an :class:`HTTPResponse` or a callable returning one."""
        self._faking = True
        self._stubs = stubs or {}
        self._recorded = []
        return self

    def stop_faking(self) -> "HTTPClient":
        self._faking = False
        self._stubs = {}
        self._recorded = []
        return self

    def is_faking(self) -> bool:
        return self._faking

    def recorded(self) -> list:
        return self._recorded

    def assert_sent(self, url: str) -> None:
        assert any(
            url in entry["url"] for entry in self._recorded
        ), f"No request was sent to a URL containing '{url}'."

    def assert_sent_count(self, count: int) -> None:
        actual = len(self._recorded)
        assert actual == count, f"Expected {count} requests sent, got {actual}."

    def assert_nothing_sent(self) -> None:
        assert not self._recorded, f"Expected no requests, got {len(self._recorded)}."

    def _record(self, entry: dict) -> None:
        self._recorded.append(entry)

    def _stub_for(self, url: str) -> HTTPResponse:
        for pattern, response in self._stubs.items():
            if pattern == "*" or pattern in url:
                return response() if callable(response) else response
        return HTTPResponse(200, b"")
