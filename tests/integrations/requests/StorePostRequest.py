from src.masonite.request import FormRequest
from src.masonite.validation import required, email


class StorePostRequest(FormRequest):
    def rules(self):
        return [
            required(["title", "author_email"]),
            email("author_email"),
        ]

    def messages(self):
        return {"title_required": "A title is required"}
