import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .Application import Application


class CoreKernel:
    """Minimal "bare-metal" kernel.

    Registers only the core framework machinery: it loads the environment,
    sets the response handler and storage path, and binds the essential
    capsules (router, middleware, loader) plus an empty command registry.
    It does not register any of the built-in craft commands.

    Subclass this when you want to build a custom root kernel with a reduced
    footprint; subclass the full ``Kernel`` when you want the standard
    installation. Every import lives inside a method so importing this module
    stays cheap.
    """

    def __init__(self, app: "Application"):
        self.application = app

    def register(self) -> None:
        """Register the core Masonite features in the project."""
        self.load_environment()
        self.register_framework()
        self.register_capsules()

    def load_environment(self) -> None:
        """Load environment variables into the application."""
        from ..environment import LoadEnvironment

        LoadEnvironment()

    def register_framework(self) -> None:
        """Set the response handler and storage path."""
        from .response_handler import response_handler

        self.application.set_response_handler(response_handler)
        self.application.use_storage_path(
            os.path.join(self.application.base_path, "storage")
        )

    def register_capsules(self) -> None:
        """Bind the minimum capsules required to boot the framework."""
        from cleo.application import Application as CommandApplication
        from .. import __version__
        from ..commands import CommandCapsule
        from ..middleware import MiddlewareCapsule
        from ..loader import Loader
        from ..routes import Router

        self.application.bind("middleware", MiddlewareCapsule())
        self.application.bind("router", Router())
        self.application.bind("loader", Loader())
        self.application.bind(
            "commands",
            CommandCapsule(CommandApplication("Masonite", __version__)),
        )
