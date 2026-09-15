#!/bin/bash
# ─── server-deploy.sh ─────────────────────────────────────────────────
# Runs ON the EC2 box (invoked by CI via SSM, or manually). Authenticates
# to ECR via the instance profile, pulls the requested image tag, restarts
# the stack, and waits for both services to become healthy.
# Required env: REGISTRY, IMAGE_TAG. Optional: FRONTEND_IMAGE_TAG (defaults to
# IMAGE_TAG), DEPLOY_ENV (production|staging, default production),
# AWS_REGION (default us-east-1).
set -euo pipefail

: "${REGISTRY:?REGISTRY env var required}"
: "${IMAGE_TAG:?IMAGE_TAG env var required}"
FRONTEND_IMAGE_TAG="${FRONTEND_IMAGE_TAG:-$IMAGE_TAG}"
DEPLOY_ENV="${DEPLOY_ENV:-production}"
AWS_REGION="${AWS_REGION:-us-east-1}"
export PATH="$PATH:/usr/local/bin"
PROJECT_ROOT="/home/ubuntu/madperfume"
export REGISTRY IMAGE_TAG FRONTEND_IMAGE_TAG PROJECT_ROOT

cd "$PROJECT_ROOT"

# Authenticate Docker to ECR using the EC2 instance profile (no static keys).
aws ecr get-login-password --region "$AWS_REGION" \
  | docker login --username AWS --password-stdin "$REGISTRY"

COMPOSE="docker compose --env-file .env \
  -f deployment/compose/docker-compose.base.yml \
  -f deployment/compose/$DEPLOY_ENV/docker-compose.yml"

# Reclaim disk from old layers before pulling new ones.
docker system prune -af --filter "until=24h" || true

# Pull the backend IMAGE_TAG and FRONTEND_IMAGE_TAG, then recreate containers.
# Migrations are applied by the backend container's entrypoint (RUN_MIGRATIONS=1)
# as a single process on startup — do NOT also migrate here, or a concurrent
# `exec migrate` races the entrypoint migrate on a fresh DB.
$COMPOSE pull
$COMPOSE up -d --force-recreate --remove-orphans

$COMPOSE ps
for attempt in $(seq 1 24); do
  if curl --fail --silent -H "X-Forwarded-Proto: https" http://127.0.0.1:8000/api/v1/health/ \
     && curl --fail --silent http://127.0.0.1:3000/api/health; then
    echo
    echo "Backend and frontend are healthy."
    break
  fi
  if [ "$attempt" -eq 24 ]; then
    echo "Services did not become healthy (backend :8000, frontend :3000)" >&2
    $COMPOSE logs --tail=100 >&2
    exit 1
  fi
  sleep 5
done
