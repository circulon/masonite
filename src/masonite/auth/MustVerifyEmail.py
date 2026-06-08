"""Email verification mixin for User models."""

import time

import pendulum

from ..auth.Sign import Sign


class MustVerifyEmail:
    """Mixin that adds email verification to a User model.

    Mix it into the User model and add a nullable ``verified_at`` column to the
    users table. The auth scaffold then sends a signed verification link on
    registration and blocks ``verified`` routes until the email is confirmed.
    """

    def verify_email(self, mail_manager, request):
        """Send a signed verification link to the user's email address."""
        from ..mail import Mailable
        from ..configuration import config

        sign = Sign()
        token = sign.sign("{0}::{1}".format(self.id, time.time()))
        scheme = request.environ.get("wsgi.url_scheme", "http")
        host = request.environ.get("HTTP_HOST", "localhost")
        link = "{0}://{1}/email/verify/{2}".format(scheme, host, token)
        user_name = getattr(self, "name", "")

        class _VerifyEmail(Mailable):
            def build(self):
                return (
                    self.subject("Please Confirm Your Email")
                    .from_(config("mail.from_address"))
                    .view(
                        "auth.mailables.verify_email",
                        {"name": user_name, "link": link},
                    )
                )

        mail_manager.mailable(_VerifyEmail().to(self.email)).send()

    def has_verified_email(self):
        """Whether the user has confirmed their email address."""
        return self.verified_at is not None

    def mark_email_as_verified(self):
        """Stamp the email as verified and persist the model."""
        self.verified_at = pendulum.now().to_datetime_string()
        self.save()
