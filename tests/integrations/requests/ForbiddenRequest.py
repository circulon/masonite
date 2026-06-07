from src.masonite.request import FormRequest


class ForbiddenRequest(FormRequest):
    def authorize(self):
        return False

    def rules(self):
        return []
