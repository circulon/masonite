import responses

from tests import TestCase
from src.masonite.facades import Config, Log


class TestExceptionLoggingListener(TestCase):
    def test_exception_event_logs_type_message_and_traceback(self):
        try:
            raise ValueError("boom")
        except ValueError as exception:
            self.application.make("event").fire(
                f"masonite.exception.{exception.__class__.__name__}", exception
            )

        self.assertConsoleOutputContains("ValueError: boom")
        self.assertConsoleOutputContains("Traceback")

    def test_exception_without_traceback_is_still_logged(self):
        exception = RuntimeError("no traceback here")
        self.application.make("event").fire(
            f"masonite.exception.{exception.__class__.__name__}", exception
        )

        self.assertConsoleOutputContains("RuntimeError: no traceback here")


class TestSlackDriver(TestCase):
    @responses.activate
    def test_slack_driver_posts_message_to_webhook(self):
        webhook_url = "https://hooks.slack.test/services/fake"
        responses.add(responses.POST, webhook_url, status=200)

        old_webhook_url = Config.get("logging.channels.slack.webhook_url")
        Config.set("logging.channels.slack.webhook_url", webhook_url)
        try:
            Log.channel("slack").error("slack message")
        finally:
            Config.set("logging.channels.slack.webhook_url", old_webhook_url)

        self.assertEqual(len(responses.calls), 1)
        self.assertIn("slack message", responses.calls[0].request.body.decode())
