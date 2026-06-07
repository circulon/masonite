from src.masonite.controllers import Controller

from tests.integrations.requests.StorePostRequest import StorePostRequest
from tests.integrations.requests.ForbiddenRequest import ForbiddenRequest


class FormRequestController(Controller):
    def store(self, request: StorePostRequest):
        # Only reached when authorization and validation both pass.
        return {"validated": request.validated()}

    def forbidden(self, request: ForbiddenRequest):
        return {"ok": True}
