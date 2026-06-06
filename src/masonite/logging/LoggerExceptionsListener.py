import traceback

from ..facades import Log


class LoggerExceptionsListener:
    def handle(self, event: str, exception: Exception = None):
        # the listener is bound to the "masonite.exception.*" wildcard so it
        # should tolerate events fired without an exception payload
        if exception is None:
            Log.error(event)
            return

        exception_type = exception.__class__.__name__
        message = f"{exception_type}: {exception}"

        # log the full traceback so exceptions carry enough information
        if exception.__traceback__ is not None:
            stack = "".join(
                traceback.format_exception(
                    type(exception), exception, exception.__traceback__
                )
            )
            message = f"{message}\n{stack}"

        Log.error(message)
