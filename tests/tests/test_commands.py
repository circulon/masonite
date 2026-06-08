from src.masonite.commands.Command import Command
from cleo.application import Application as CommandApplication
from src.masonite.commands import CommandCapsule
from tests import TestCase


class FakeTestCommand(Command):
    """
    Command for testing command assertions only.
    fake_test_command
        {--f|--fail : Make command fail}
    """

    def handle(self):
        self.info("Command success !")


class TestCommandsAssertions(TestCase):
    def setUp(self):
        super().setUp()
        self.original_commands = self.application.make("commands")
        command_app = CommandCapsule(CommandApplication("Masonite Version:", "tests"))
        self.application.bind("commands", command_app)
        self.application.make("commands").add(FakeTestCommand())

    def tearDown(self):
        super().tearDown()
        self.application.bind("commands", self.original_commands)

    def test_running_command_during_tests(self):
        self.craft("fake_test_command")

    def test_assert_output(self):
        self.craft("fake_test_command").assertOutputContains("Command")
        self.craft("fake_test_command").assertExactOutput("Command success !\n")

    def test_assert_output_missing(self):
        self.craft("fake_test_command").assertOutputMissing(
            "This is not in the command"
        )

    def test_assert_errors(self):
        with self.assertRaises(AssertionError):
            self.craft("fake_test_command").assertHasErrors()

    def test_assert_success(self):
        self.craft("fake_test_command").assertSuccess()


class TestCommandCapsuleEnabled(TestCase):
    def make_capsule(self, enabled):
        return CommandCapsule(
            CommandApplication("Masonite Version:", "tests"), enabled=enabled
        )

    def test_enabled_by_default(self):
        capsule = CommandCapsule(CommandApplication("Masonite Version:", "tests"))
        capsule.add(FakeTestCommand())
        self.assertIn("fake_test_command", capsule.command_name)

    def test_disabled_capsule_ignores_add(self):
        capsule = self.make_capsule(enabled=False)
        result = capsule.add(FakeTestCommand())

        self.assertIs(result, capsule)
        self.assertEqual(capsule.command_name, [])

    def test_disabled_capsule_ignores_swap(self):
        capsule = self.make_capsule(enabled=False)
        capsule.swap(FakeTestCommand())

        self.assertEqual(capsule.command_name, [])
