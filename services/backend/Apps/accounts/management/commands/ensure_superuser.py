"""Idempotently create a Django superuser from environment variables.

Designed to run on every container start (e.g. from entrypoint.sh): it creates
the superuser only if one with that email does not already exist, so restarts
never fail. The stock ``createsuperuser --noinput`` is unsuitable here because
it errors when the user already exists and does not understand this project's
email-based custom user model.

Environment variables:
    DJANGO_SUPERUSER_EMAIL            (required) login email — the USERNAME_FIELD
    DJANGO_SUPERUSER_PASSWORD         (required)
    DJANGO_SUPERUSER_FULL_NAME       (optional) defaults to the email local-part
    DJANGO_SUPERUSER_UPDATE_PASSWORD (optional) "1" -> reset the password if the
                                     user already exists (default: leave as-is)

If email or password is missing, the command no-ops (does not fail), so it is
safe to wire into the startup of every environment.
"""

import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import IntegrityError, transaction


class Command(BaseCommand):
    help = "Create a superuser from DJANGO_SUPERUSER_* env vars if one is missing."

    def handle(self, *args, **options):
        User = get_user_model()

        email = (os.environ.get("DJANGO_SUPERUSER_EMAIL") or "").strip()
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD") or ""

        if not email or not password:
            self.stdout.write(
                "DJANGO_SUPERUSER_EMAIL / DJANGO_SUPERUSER_PASSWORD not set — "
                "skipping superuser bootstrap."
            )
            return

        email = User.objects.normalize_email(email)
        full_name = (
            os.environ.get("DJANGO_SUPERUSER_FULL_NAME") or email.split("@", 1)[0]
        )

        existing = User.objects.filter(email__iexact=email).first()
        if existing is not None:
            if os.environ.get("DJANGO_SUPERUSER_UPDATE_PASSWORD") == "1":
                existing.set_password(password)
                existing.is_staff = True
                existing.is_superuser = True
                existing.save(update_fields=["password", "is_staff", "is_superuser"])
                self.stdout.write(
                    self.style.WARNING(f"Superuser {email} existed — password reset.")
                )
            else:
                self.stdout.write(f"Superuser {email} already exists — nothing to do.")
            return

        try:
            with transaction.atomic():
                User.objects.create_superuser(
                    email=email, password=password, full_name=full_name
                )
        except IntegrityError:
            # Another starting replica won the race; that's fine.
            self.stdout.write(f"Superuser {email} created concurrently — skipping.")
            return

        self.stdout.write(self.style.SUCCESS(f"Created superuser {email}."))
