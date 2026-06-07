from masonite.request import FormRequest
from masonite.validation import required


class __class__(FormRequest):
    """Form request for __class__."""

    def authorize(self) -> bool:
        """Determine if the user is allowed to make this request."""
        return True

    def rules(self) -> list:
        """The validation rules applied to the request input."""
        return [
            required(["example"]),
        ]

    def messages(self) -> dict:
        """Custom validation messages keyed by ``field_rule``."""
        return {}
