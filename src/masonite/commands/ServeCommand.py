import logging
import os
import shutil
import sys
from datetime import datetime
from urllib.parse import urlparse, urlunparse

from werkzeug.serving import WSGIRequestHandler, run_simple

from ..utils.console import MUTED, VIOLET, VIOLET_LIT, paint, supports_ansi
from .Command import Command


class QuietWerkzeugFilter(logging.Filter):
    """Replace werkzeug's startup noise (development server warning, addresses,
    reloader chatter) with the styled banner printed by ServeCommand. Errors
    are always kept, and file-change reloads are restyled as a single line."""

    def filter(self, record):
        if record.levelno >= logging.ERROR:
            return True

        message = record.getMessage()
        if "Detected change" in message:
            detail = message.strip().lstrip("* ")
            if supports_ansi():
                print(f"  {paint('↻', VIOLET, bold=True)} {paint(detail, MUTED)}")
            else:
                print(f"  {detail}")
        return False


class StyledRequestHandler(WSGIRequestHandler):
    """Log requests Laravel-style: time, method and path with the status
    dotted out to the right edge of the terminal."""

    def log_request(self, code="-", size="-"):
        try:
            path = self.path
            method = self.command
        except AttributeError:
            path = self.requestline
            method = ""

        now = datetime.now().strftime("%H:%M:%S")
        status = str(code)

        if not supports_ansi():
            print(f"  [{now}] {method} {path} {status}")
            return

        try:
            status_class = int(status) // 100
        except ValueError:
            status_class = 0
        status_colors = {2: VIOLET_LIT, 3: MUTED, 4: (227, 179, 65), 5: (227, 79, 79)}
        status_rgb = status_colors.get(status_class)

        left = f"  {now}  {method.ljust(7)} {path} "
        right = f" {status}"
        columns = shutil.get_terminal_size().columns
        dots = "." * max(columns - len(left) - len(right) - 2, 3)

        print(
            paint(f"  {now}", MUTED)
            + f"  {paint(method.ljust(7), bold=True)} {path} "
            + paint(dots, MUTED)
            + " "
            + paint(status, status_rgb, bold=True)
        )


class ServeCommand(Command):
    """
    Run the Masonite server.

    serve
        {--p|port=8000 : Specify which port to run the server}
        {--b|host=127.0.0.1 : Specify which ip address to run the server}
        {--d|dont-reload : Make the server NOT automatically reload on file changes}
        {--i|reload-interval=1 : Number of seconds to wait to reload after changed are detected}
        {--l|live-reload : Make the server automatically refresh your web browser}
        {--t|threaded : Handle concurrent requests using threads}
    """

    def __init__(self, application):
        super().__init__()
        self.app = application

    def _sync_app_url(self, host, port):
        """Point ``application.app_url`` at the address the server binds to.

        URLs generated while the dev server runs (``url()``, ``asset()``, mail
        links, ...) are derived from ``application.app_url``. When ``serve`` is
        given a custom ``--host``/``--port`` we rewrite the host and port of the
        configured URL — preserving its scheme, path and any credentials — so
        those generated links actually resolve to the running server.
        """
        config = self.app.make("config")
        app_url = config.get("application.app_url")
        if not app_url:
            return

        parsed = urlparse(app_url)
        if not parsed.scheme or not parsed.netloc:
            # Not a full URL (e.g. just a host name) — leave it untouched
            # rather than risk mangling it.
            return

        netloc = f"{host}:{port}"
        if parsed.username:
            credentials = parsed.username
            if parsed.password:
                credentials = f"{credentials}:{parsed.password}"
            netloc = f"{credentials}@{netloc}"

        config.set("application.app_url", urlunparse(parsed._replace(netloc=netloc)))

    def handle(self):
        self._sync_app_url(self.option("host"), self.option("port"))

        if self.option("live-reload"):
            try:
                from livereload import Server
            except ImportError:
                raise ImportError(
                    "Could not find the livereload library. Install it by running 'pip install livereload==2.5.1'"
                )

            import glob

            server = Server(self.app)
            for filepath in glob.glob("resources/templates/**/*/"):
                server.watch(filepath)

            self.line("")
            self.info("Live reload server is starting...")
            self.info(
                "This will only work for templates. Changes to Python files may require a browser refresh."
            )
            self.line("")
            server.serve(
                port=self.option("port"),
                restart_delay=self.option("reload-interval"),
                liveport=5500,
                root=self.app.base_path,
                debug=True,
            )
            return

        host = self.option("host")
        port = int(self.option("port"))
        use_reloader = not self.option("dont-reload")
        threaded = bool(self.option("threaded"))
        extra_files = [".env", self.app.get_storage_path()]

        logging.getLogger("werkzeug").addFilter(QuietWerkzeugFilter())

        # with the reloader enabled werkzeug re-runs this command in a child
        # process (WERKZEUG_RUN_MAIN=true): only print the banner once
        if os.environ.get("WERKZEUG_RUN_MAIN") != "true":
            self._banner(host, port, use_reloader)

        run_simple(
            host,
            port,
            self.app,
            threaded=threaded,
            use_reloader=use_reloader,
            extra_files=extra_files,
            request_handler=StyledRequestHandler,
            # more efficient than stat
            reloader_type="watchdog",
        )

    def _banner(self, host, port, use_reloader):
        from .. import __version__

        url = f"http://{host}:{port}"
        reload_note = (
            "auto-reload on file changes" if use_reloader else "auto-reload disabled"
        )

        if not (supports_ansi() and "utf" in (sys.stdout.encoding or "").lower()):
            self.info(f"Masonite v{__version__} development server")
            self.info(f"Server running at {url} ({reload_note}, Ctrl+C to stop)")
            self.line("")
            return

        print()
        print(
            f"  {paint('➜', VIOLET, bold=True)} "
            + paint("Masonite", VIOLET, bold=True)
            + paint(f" v{__version__}", MUTED)
            + "  Server running at "
            + paint(url, VIOLET_LIT, bold=True)
        )
        print(paint(f"    {reload_note} — press Ctrl+C to stop", MUTED))
        print()
