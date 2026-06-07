"""New Form Request Command."""
import inflection
import os

from ..utils.filesystem import make_directory, render_stub_file, get_module_dir
from ..utils.location import requests_path
from .Command import Command


class MakeRequestCommand(Command):
    """
    Creates a new form request class.

    request
        {name : Name of the form request}
        {--f|force=? : Force overriding file if already exists}
    """

    def __init__(self, application):
        super().__init__()
        self.app = application

    def handle(self):
        name = inflection.camelize(self.argument("name"))
        content = render_stub_file(self.get_stub_request_path(), name)

        filename = f"{name}.py"
        filepath = requests_path(filename)
        make_directory(filepath)
        if os.path.exists(filepath) and not self.option("force"):
            self.warning(
                f"{filepath} already exists! Run the command with -f (force) to override."
            )
            return -1
        with open(filepath, "w") as f:
            f.write(content)

        # add class to __init__.py
        with open(os.path.join(os.path.dirname(filepath), "__init__.py"), "a") as f:
            f.write(f"from .{name} import {name}\n")

        self.info(f"Form Request Created ({requests_path(filename, absolute=False)})")

    def get_stub_request_path(self):
        return os.path.join(get_module_dir(__file__), "../stubs/requests/FormRequest.py")
