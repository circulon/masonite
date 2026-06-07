import os
import sys

# Masonite brand colors (see .github/logo/masonite-mark.svg)
VIOLET = (109, 79, 227)  # #6d4fe3 — interactive
VIOLET_LIT = (156, 130, 242)  # #9c82f2 — lit face
VIOLET_DEEP = (74, 51, 166)  # #4a33a6 — deep face
MUTED = (94, 98, 106)  # #5e626a


def supports_ansi():
    return (
        sys.stdout.isatty()
        and os.environ.get("NO_COLOR") is None
        and os.environ.get("TERM", "") != "dumb"
    )


def paint(text, rgb=None, bold=False):
    """Color a string with truecolor ANSI codes when the terminal supports it."""
    if not supports_ansi() or (rgb is None and not bold):
        return text
    prefix = ""
    if rgb is not None:
        prefix += "\x1b[38;2;{0};{1};{2}m".format(*rgb)
    if bold:
        prefix += "\x1b[1m"
    return f"{prefix}{text}\x1b[0m"


class HasColoredOutput:
    """Add level-colored output print functions to a class."""

    def success(self, message):
        print("\033[92m {0} \033[0m".format(message))

    def warning(self, message):
        print("\033[93m {0} \033[0m".format(message))

    def danger(self, message):
        print("\033[91m {0} \033[0m".format(message))

    def info(self, message):
        return self.success(message)


class AddCommandColors:
    """The default style set used by Cleo is defined here:
    https://github.com/sdispater/clikit/blob/master/src/clikit/formatter/default_style_set.py
    This mixin add method helper to output errors and warnings.
    """

    def error(self, text):
        """
        Write a string as information output.

        :param text: The line to write
        :type text: str
        """
        self.line(text, "error")

    def warning(self, text):
        """
        Write a string as information output.

        :param text: The line to write
        :type text: str
        """
        self.line(text, "c2")
