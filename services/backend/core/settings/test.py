"""Test settings — fast and isolated."""

import tempfile

from .base import *  # noqa: F401,F403
from .base import REST_FRAMEWORK

DEBUG = False

MEDIA_ROOT = tempfile.mkdtemp(prefix="madperfume-test-media-")

# Always an isolated in-memory SQLite database, even if DATABASE_URL is exported.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

SECRET_KEY = "test-secret-key-not-for-production"

REST_FRAMEWORK = {
    **REST_FRAMEWORK,
    "DEFAULT_THROTTLE_RATES": {"anon": None, "user": None},
}

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
