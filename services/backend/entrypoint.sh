#!/usr/bin/env bash
###############################################################################
# Mad Perfume backend container entrypoint.
#
# Responsibilities (in order):
#   1. Wait for PostgreSQL (and Redis, if configured) to accept connections.
#   2. Apply database migrations.
#   3. Collect static files (opt-in; prod images bake these at build time).
#   4. Ensure runtime directories exist.
#   5. Hand off (exec) to the requested process so it becomes PID 1's child
#      and receives signals directly for clean shutdowns.
#
# Dispatch (first argument):
#   gunicorn     -> production WSGI server
#   runserver    -> Django dev server with autoreload
#   <anything>   -> executed verbatim (e.g. management commands, the scheduler)
###############################################################################
set -Eeuo pipefail

log() { printf '[entrypoint] %s\n' "$*"; }
die() { printf '[entrypoint] ERROR: %s\n' "$*" >&2; exit 1; }

# --- Configuration (all overridable via environment) ------------------------
export DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-core.settings.prod}"
: "${WAIT_FOR_DB:=1}"
: "${DB_WAIT_TIMEOUT:=60}"
: "${WAIT_FOR_REDIS:=1}"
: "${RUN_MIGRATIONS:=1}"
: "${RUN_COLLECTSTATIC:=0}"
# Bootstrap a superuser from DJANGO_SUPERUSER_* env vars (idempotent; the
# command no-ops if email/password are unset). Set CREATE_SUPERUSER=0 to skip.
: "${CREATE_SUPERUSER:=1}"

: "${GUNICORN_BIND:=0.0.0.0:8000}"
: "${GUNICORN_WORKERS:=3}"
: "${GUNICORN_THREADS:=2}"
: "${GUNICORN_TIMEOUT:=60}"
: "${GUNICORN_GRACEFUL_TIMEOUT:=30}"
: "${GUNICORN_MAX_REQUESTS:=1000}"
: "${GUNICORN_MAX_REQUESTS_JITTER:=100}"
: "${GUNICORN_LOG_LEVEL:=info}"

# Some PaaS platforms inject $PORT; honor it for the bind address.
if [[ -n "${PORT:-}" ]]; then
  GUNICORN_BIND="0.0.0.0:${PORT}"
fi

# --- 1. Wait for dependent services -----------------------------------------
wait_for_db() {
  [[ "${WAIT_FOR_DB}" == "1" ]] || { log "Skipping DB wait (WAIT_FOR_DB=0)."; return; }
  log "Waiting for the database (timeout ${DB_WAIT_TIMEOUT}s)..."
  DB_WAIT_TIMEOUT="${DB_WAIT_TIMEOUT}" python <<'PY'
import os, sys, time
import django
from django.db import connections
from django.db.utils import OperationalError

django.setup()  # reads DJANGO_SETTINGS_MODULE from the environment
deadline = time.time() + float(os.environ.get("DB_WAIT_TIMEOUT", "60"))
while True:
    try:
        connections["default"].ensure_connection()
        print("[entrypoint] database is up.")
        break
    except OperationalError as exc:
        if time.time() > deadline:
            sys.exit(f"[entrypoint] database unreachable: {exc}")
        time.sleep(1)
PY
}

wait_for_redis() {
  [[ "${WAIT_FOR_REDIS}" == "1" && -n "${REDIS_URL:-}" ]] || return 0
  log "Waiting for Redis at ${REDIS_URL}..."
  python <<'PY'
import os, sys, time
import redis

url = os.environ["REDIS_URL"]
deadline = time.time() + 30
while True:
    try:
        redis.Redis.from_url(url).ping()
        print("[entrypoint] redis is up.")
        break
    except Exception as exc:  # noqa: BLE001 - any connection error retries
        if time.time() > deadline:
            sys.exit(f"[entrypoint] redis unreachable: {exc}")
        time.sleep(1)
PY
}

# --- 2-4. One-time startup tasks --------------------------------------------
run_startup_tasks() {
  mkdir -p /app/media /app/staticfiles

  if [[ "${RUN_MIGRATIONS}" == "1" ]]; then
    log "Applying database migrations..."
    python manage.py migrate --noinput
  else
    log "Skipping migrations (RUN_MIGRATIONS=0)."
  fi

  if [[ "${CREATE_SUPERUSER}" == "1" ]]; then
    log "Ensuring superuser exists (from DJANGO_SUPERUSER_* env)..."
    python manage.py ensure_superuser
  fi

  if [[ "${RUN_COLLECTSTATIC}" == "1" ]]; then
    log "Collecting static files..."
    python manage.py collectstatic --noinput
  fi
}

# --- 5. Dispatch ------------------------------------------------------------
main() {
  local cmd="${1:-gunicorn}"

  case "${cmd}" in
    gunicorn)
      wait_for_db
      wait_for_redis
      run_startup_tasks
      log "Starting gunicorn on ${GUNICORN_BIND} (${GUNICORN_WORKERS} workers)..."
      exec gunicorn core.wsgi:application \
        --bind "${GUNICORN_BIND}" \
        --workers "${GUNICORN_WORKERS}" \
        --threads "${GUNICORN_THREADS}" \
        --timeout "${GUNICORN_TIMEOUT}" \
        --graceful-timeout "${GUNICORN_GRACEFUL_TIMEOUT}" \
        --max-requests "${GUNICORN_MAX_REQUESTS}" \
        --max-requests-jitter "${GUNICORN_MAX_REQUESTS_JITTER}" \
        --forwarded-allow-ips '*' \
        --access-logfile - \
        --error-logfile - \
        --log-level "${GUNICORN_LOG_LEVEL}"
      ;;

    runserver)
      wait_for_db
      wait_for_redis
      run_startup_tasks
      log "Starting Django development server (autoreload) on 0.0.0.0:8000..."
      exec python manage.py runserver 0.0.0.0:8000
      ;;

    *)
      # Arbitrary command (management commands, scheduler loop, shell, ...).
      # Still wait for the DB so jobs don't race a cold database.
      wait_for_db
      log "Executing: $*"
      exec "$@"
      ;;
  esac
}

main "$@"
