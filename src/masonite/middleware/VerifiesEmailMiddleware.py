from .middleware import Middleware


class VerifiesEmailMiddleware(Middleware):
    """Block a route until the authenticated user has a verified email.

    Register it as ``verified`` and add it to routes that should be reachable
    only by verified users. Unauthenticated visitors are sent to ``/login`` and
    unverified ones to the verification notice page.
    """

    def before(self, request, response):
        user = request.user()
        if not user:
            return response.redirect("/login")
        if not hasattr(user, "has_verified_email") or not user.has_verified_email():
            return response.redirect("/email/verify/notice")
        return request

    def after(self, request, response):
        return request
