from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

EMAILS = {
    "reset": {
        "subject": "Reset your Mad Perfume admin password",
        "heading": "Reset your password",
        "intro": "we received a request to reset the password for your Mad Perfume admin account.",
        "button": "RESET PASSWORD",
    },
    "invite": {
        "subject": "Welcome to the Mad Perfume team",
        "heading": "Set up your account",
        "intro": "you've been added to the Mad Perfume admin team. Choose a password to activate your account.",
        "button": "SET PASSWORD",
    },
}


def send_password_link(user, kind="reset"):
    """Emails a single-use link to /reset-password (used for resets and staff invites)."""
    copy = EMAILS[kind]
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    link = f"{settings.ADMIN_URL}/reset-password?uid={uid}&token={default_token_generator.make_token(user)}"
    hours = settings.PASSWORD_RESET_TIMEOUT // 3600
    context = {**copy, "name": user.full_name, "link": link, "logo_url": f"{settings.ADMIN_URL}/logo.png",
               "expires": f"{hours} hour{'s' if hours != 1 else ''}"}
    send_mail(
        copy["subject"],
        f"{copy['heading']}:\n\n{link}\n\nThe link expires in {context['expires']}. If you weren't expecting this, you can ignore this email.",
        None,
        [user.email],
        html_message=render_to_string("accounts/emails/password_reset.html", context),
    )
