import json as json_lib


class HTTPResponse:
    """A lightweight wrapper around an HTTP response.

    Wraps a ``requests`` response for real calls and is also constructed
    directly to build fake responses in tests.
    """

    def __init__(self, status_code: int = 200, body=b"", headers: dict = None):
        self.status_code = status_code
        if isinstance(body, (dict, list)):
            body = json_lib.dumps(body)
        self._body = body if isinstance(body, bytes) else str(body).encode("utf-8")
        self.headers = headers or {}

    @classmethod
    def from_requests(cls, response) -> "HTTPResponse":
        return cls(response.status_code, response.content, dict(response.headers))

    def body(self) -> bytes:
        return self._body

    def text(self) -> str:
        return self._body.decode("utf-8", errors="replace")

    def json(self):
        return json_lib.loads(self._body or b"null")

    def header(self, name: str, default=None):
        return self.headers.get(name, default)

    def status(self) -> int:
        return self.status_code

    def ok(self) -> bool:
        return 200 <= self.status_code < 300

    # `successful` reads better at call sites; keep `ok` as the short alias.
    def successful(self) -> bool:
        return self.ok()

    def failed(self) -> bool:
        return not self.ok()

    def client_error(self) -> bool:
        return 400 <= self.status_code < 500

    def server_error(self) -> bool:
        return 500 <= self.status_code < 600
