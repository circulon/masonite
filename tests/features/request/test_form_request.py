import os

from tests import TestCase
from src.masonite.routes import Route
from src.masonite.exceptions import AuthorizationException
from src.masonite.utils.location import requests_path


class TestFormRequest(TestCase):
    def setUp(self):
        super().setUp()
        self.withExceptionsHandling()
        self.addRoutes(
            Route.post("/posts", "FormRequestController@store"),
            Route.post("/forbidden", "FormRequestController@forbidden"),
        )

    def test_passing_validation_runs_the_controller(self):
        self.post(
            "/posts", {"title": "My Post", "author_email": "author@example.com"}
        ).assertOk().assertJson(
            {"validated": {"title": "My Post", "author_email": "author@example.com"}}
        )

    def test_validated_returns_only_ruled_fields(self):
        # `extra` has no rule, so it must not leak into validated().
        self.post(
            "/posts",
            {"title": "My Post", "author_email": "author@example.com", "extra": "x"},
        ).assertJsonMissing("validated.extra")

    def test_failing_validation_redirects_back_with_errors(self):
        self.post("/posts", {"author_email": "not-an-email"}).assertRedirect()
        # title is required and author_email is not a valid email
        self.assertTrue(self.application.make("request").session.has("errors"))

    def test_failing_validation_returns_422_for_json(self):
        (
            self.withHeaders({"Accept": "application/json"})
            .post("/posts", {"author_email": "not-an-email"})
            .assertIsStatus(422)
            .assertJsonPath("message", "The given data was invalid.")
        )

    def test_unauthorized_request_raises_authorization_exception(self):
        # authorize() returning False raises AuthorizationException, which the
        # framework renders as a 403 (covered by the gate tests). Here we assert
        # the request never reaches the controller.
        self.withoutExceptionsHandling()
        with self.assertRaises(AuthorizationException):
            self.post("/forbidden", {})


class TestMakeRequestCommand(TestCase):
    def test_command_creates_a_form_request(self):
        init_file = requests_path("__init__.py")
        original_init = ""
        if os.path.exists(init_file):
            with open(init_file) as f:
                original_init = f.read()

        target = requests_path("FakeGeneratedRequest.py")
        try:
            self.craft("request", "FakeGeneratedRequest")
            self.assertTrue(os.path.exists(target))
            with open(target) as f:
                content = f.read()
            self.assertIn("class FakeGeneratedRequest(FormRequest)", content)
        finally:
            if os.path.exists(target):
                os.remove(target)
            with open(init_file, "w") as f:
                f.write(original_init)
