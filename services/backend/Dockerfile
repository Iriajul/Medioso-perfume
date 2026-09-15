###############################################################################
# Mad Perfume backend — multi-stage image (Django 6 + DRF on Python 3.13, uv).
#
# Stages:
#   base    — slim Python runtime + minimal OS deps (curl for healthcheck)
#   builder — resolves dependencies into /app/.venv from the locked uv.lock
#   dev     — hot-reloading dev server, source bind-mounted by compose
#   prod    — immutable, non-root, gunicorn + WhiteNoise, static baked in
#
# Build a target explicitly:
#   docker build --target prod -t madperfume-backend:prod .
#   docker build --target dev  -t madperfume-backend:dev  .
###############################################################################

ARG PYTHON_VERSION=3.13
ARG UV_VERSION=0.11.12

# Pinned uv binary, copied into the builder (keeps it out of the runtime image).
FROM ghcr.io/astral-sh/uv:${UV_VERSION} AS uv


###############################################################################
# base — shared runtime foundation
###############################################################################
FROM python:${PYTHON_VERSION}-slim-bookworm AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    # uv: copy (not hardlink) into the venv so it survives across stages/mounts,
    # compile .pyc at install time for faster cold starts, and pin the venv path.
    UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PYTHON_DOWNLOADS=never \
    UV_PROJECT_ENVIRONMENT=/app/.venv \
    PATH="/app/.venv/bin:${PATH}"

# curl: used by the container HEALTHCHECK. psycopg ships a binary wheel, so no
# libpq / build toolchain is needed at runtime.
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app


###############################################################################
# builder — install third-party dependencies (cached on lockfile changes)
###############################################################################
FROM base AS builder

COPY --from=uv /uv /uvx /usr/local/bin/

# Dependency layer: only the manifests, so this layer is reused until
# pyproject.toml / uv.lock actually change. --no-install-project keeps the app
# itself out of the venv (it is imported from the working directory instead),
# so app-code edits never invalidate the dependency layer.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

# Application source. Anything excluded by .dockerignore (host .venv, .env,
# .git, caches, media, staticfiles) never enters the image.
COPY . .


###############################################################################
# dev — hot reload; source is bind-mounted over /app by docker-compose.dev.yml
###############################################################################
FROM builder AS dev

ENV DJANGO_SETTINGS_MODULE=core.settings.dev \
    RUN_COLLECTSTATIC=0

COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

EXPOSE 8000
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["runserver"]


###############################################################################
# prod — minimal, non-root, immutable; gunicorn serving WSGI + WhiteNoise
###############################################################################
FROM base AS prod

ENV DJANGO_SETTINGS_MODULE=core.settings.prod \
    RUN_MIGRATIONS=1 \
    RUN_COLLECTSTATIC=0 \
    GUNICORN_WORKERS=3 \
    GUNICORN_BIND=0.0.0.0:8000

# Unprivileged runtime user (fixed uid/gid for predictable volume ownership;
# no login shell, no home creation — /app is supplied by the COPY below).
RUN groupadd --gid 1000 app \
    && useradd --uid 1000 --gid 1000 --home-dir /app --no-create-home \
        --shell /usr/sbin/nologin app

# Pull in the resolved venv and application source from the builder.
COPY --from=builder --chown=app:app /app /app
COPY --chown=app:app entrypoint.sh /usr/local/bin/entrypoint.sh

# Bake static assets into the image (WhiteNoise manifest), prepare writable
# runtime dirs, and lock down the entrypoint. SECRET_KEY is only needed to
# import settings here; a throwaway value is fine — collectstatic touches no
# secret-bearing code path and no database.
RUN chmod +x /usr/local/bin/entrypoint.sh \
    && mkdir -p /app/staticfiles /app/media \
    && SECRET_KEY="build-only-not-used-at-runtime" \
       DATABASE_URL="postgres://u:p@localhost:5432/db" \
       ALLOWED_HOSTS="localhost" \
       python manage.py collectstatic --noinput \
    && chown -R app:app /app/staticfiles /app/media

USER app

EXPOSE 8000

# Probe over plain HTTP; the forwarded-proto header keeps the SSL redirect from
# firing, and the health path is also exempt from redirects in prod settings.
HEALTHCHECK --interval=30s --timeout=5s --start-period=40s --retries=3 \
    CMD curl -fsS -H "X-Forwarded-Proto: https" \
        http://127.0.0.1:8000/api/v1/health/ || exit 1

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["gunicorn"]
