"""Production (and staging) settings.

Everything sensitive is required from the environment (no insecure defaults).
Runs inside a container behind nginx, which terminates TLS.
"""

from .base import *  # noqa: F401,F403
from .base import ALLOWED_HOSTS, MIDDLEWARE, env

DEBUG = False

# ---------------------------------------------------------------------------
# Database — AWS RDS PostgreSQL (required; no SQLite fallback in production).
#   postgres://USER:PASS@<rds-endpoint>:5432/madperfume?sslmode=require
# ---------------------------------------------------------------------------
DATABASES = {"default": env.db_url("DATABASE_URL")}
DATABASES["default"]["CONN_MAX_AGE"] = env.int("DB_CONN_MAX_AGE", default=60)
DATABASES["default"]["CONN_HEALTH_CHECKS"] = True

# Keep loopback reachable so the container HEALTHCHECK (127.0.0.1) passes host
# validation even when ALLOWED_HOSTS only lists the public domain.
ALLOWED_HOSTS = list(dict.fromkeys([*ALLOWED_HOSTS, "127.0.0.1", "localhost"]))

# ---------------------------------------------------------------------------
# Security hardening — relies on TLS termination in front of the app.
# ---------------------------------------------------------------------------
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=True)
SECURE_REDIRECT_EXEMPT = [r"^api/v1/health/?$"]
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = env.int("SECURE_HSTS_SECONDS", default=60 * 60 * 24 * 30)
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# ---------------------------------------------------------------------------
# Static files — WhiteNoise, right after SecurityMiddleware.
# ---------------------------------------------------------------------------
MIDDLEWARE = list(MIDDLEWARE)
MIDDLEWARE.insert(
    MIDDLEWARE.index("django.middleware.security.SecurityMiddleware") + 1,
    "whitenoise.middleware.WhiteNoiseMiddleware",
)

# Media (product images, banners). S3 when a bucket is configured — the EC2
# instance role already has read/write on it — otherwise the media_data volume.
AWS_STORAGE_BUCKET_NAME = env("AWS_STORAGE_BUCKET_NAME", default="")
if AWS_STORAGE_BUCKET_NAME:
    _default_storage = {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            "bucket_name": AWS_STORAGE_BUCKET_NAME,
            "region_name": env("AWS_S3_REGION_NAME", default="us-east-1"),
            "location": "media",
            "querystring_auth": False,
        },
    }
else:
    _default_storage = {"BACKEND": "django.core.files.storage.FileSystemStorage"}

STORAGES = {
    "default": _default_storage,
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}

# ---------------------------------------------------------------------------
# Cache — Redis when configured (shared throttle counters across workers).
# ---------------------------------------------------------------------------
REDIS_URL = env("REDIS_URL", default="")
if REDIS_URL:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.redis.RedisCache",
            "LOCATION": REDIS_URL,
        }
    }
