from ..exceptions.exceptions import AuthorizationException, ValidationException
from .request import Request


class FormRequest:
    """Base class for self-authorizing, self-validating form requests.

    Type-hint a subclass in a controller method and the container builds it,
    runs :meth:`authorize` and then validates the incoming input against
    :meth:`rules` before the controller body runs:

    ```python
    from masonite.request import FormRequest
    from masonite.validation import required, email

    class StorePostRequest(FormRequest):
        def authorize(self):
            return self.user() is not None

        def rules(self):
            return [required(["title", "body"]), email("author_email")]

    class PostController(Controller):
        def store(self, request: StorePostRequest):
            data = request.validated()
            ...
    ```

    An ``authorize()`` that returns ``False`` raises an
    :class:`AuthorizationException` (``403``). Failing validation raises a
    :class:`ValidationException`, which is rendered as a redirect back with the
    errors flashed to the session, or a ``422`` JSON response for requests that
    accept JSON.
    """

    def __init__(self, request: Request):
        self.request = request
        self.application = request.app
        self._validated = {}
        self.handle()

    # -- Overridable hooks -------------------------------------------------
    def authorize(self) -> bool:
        """Return ``True`` to allow the request. Override to gate the action."""
        return True

    def rules(self) -> list:
        """Return the validation rules to apply to the request input."""
        return []

    def messages(self) -> dict:
        """Return custom validation messages keyed by ``field_rule``."""
        return {}

    # -- Convenience accessors (delegate to the underlying request) --------
    def all(self) -> dict:
        return self.request.all()

    def input(self, name: str, default: str = ""):
        return self.request.input(name, default)

    def user(self):
        return self.request.user()

    def validated(self) -> dict:
        """Return only the inputs that were covered by a validation rule."""
        return self._validated

    # -- Internals ---------------------------------------------------------
    def handle(self) -> None:
        if not self.authorize():
            raise AuthorizationException()

        rules = self.rules()
        if not isinstance(rules, (list, tuple)):
            rules = [rules]

        errors = self.request.validate(*rules, messages=self.messages())
        if errors.any():
            raise ValidationException(errors)

        self._validated = self._collect_validated(rules)

    def _collect_validated(self, rules) -> dict:
        keys = []
        for rule in rules:
            fields = getattr(rule, "validations", None)
            if fields:
                keys.extend(fields)
        inputs = self.request.all()
        return {key: inputs[key] for key in keys if key in inputs}
