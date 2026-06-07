from ...facades import Session


class ValidationExceptionHandler:
    """Turns a ValidationException raised by a FormRequest into a response.

    A request that accepts JSON gets a ``422`` payload with the error bag. Any
    other request has its errors and old input flashed to the session and is
    redirected back to the previous page, matching the behaviour of the
    ``request.validate()`` / ``response.back().with_errors()`` flow.
    """

    def __init__(self, application):
        self.application = application

    def handle(self, exception):
        response = self.application.make("response")
        request = self.application.make("request")

        errors = exception.errors
        error_dict = errors.all() if hasattr(errors, "all") else errors

        if request.accepts_json():
            return response.json(
                {"message": exception.message, "errors": error_dict},
                exception.status,
            )

        Session.flash("errors", error_dict)
        for key, value in request.all().items():
            Session.flash(key, value)

        return response.back()
