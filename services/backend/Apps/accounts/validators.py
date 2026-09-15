import re

from django.core.exceptions import ValidationError


class ComplexityValidator:
    """At least one number and one special character (Security Settings requirements)."""

    def validate(self, password, user=None):
        if not re.search(r"\d", password):
            raise ValidationError("Password must contain at least one number (0-9).", code="password_no_number")
        if not re.search(r"[^A-Za-z0-9]", password):
            raise ValidationError("Password must contain at least one special character (!@#$%).", code="password_no_symbol")

    def get_help_text(self):
        return "Your password must contain at least one number and one special character."
