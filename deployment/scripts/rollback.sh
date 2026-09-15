#!/bin/bash
# ─── rollback.sh ──────────────────────────────────────────────────────
# Roll Mad Perfume production back to previous image tags in ECR.
# Usage:  REGISTRY=<acct>.dkr.ecr.us-east-1.amazonaws.com \
#         EC2_HOST=<ec2-public-ip> ./rollback.sh <backend-git-sha> [frontend-git-sha]
set -euo pipefail

BACKEND_TAG="${1:?Usage: ./rollback.sh <backend-git-sha> [frontend-git-sha]}"
FRONTEND_IMAGE_TAG="${2:-${FRONTEND_IMAGE_TAG:-$BACKEND_TAG}}"
PROJECT_NAME="${PROJECT_NAME:-madperfume}"
REGISTRY="${REGISTRY:?REGISTRY env var required (your ECR registry URL)}"
EC2_HOST="${EC2_HOST:?EC2_HOST env var required}"
AWS_REGION="${AWS_REGION:-us-east-1}"

echo "▶ Rolling back Mad Perfume: backend=$BACKEND_TAG, frontend=$FRONTEND_IMAGE_TAG"

ssh -i ~/.ssh/id_rsa "ubuntu@$EC2_HOST" << EOF
  set -euo pipefail
  cd /home/ubuntu/$PROJECT_NAME
  export PATH=\$PATH:/usr/local/bin
  export REGISTRY='$REGISTRY'
  export IMAGE_TAG='$BACKEND_TAG'
  export FRONTEND_IMAGE_TAG='$FRONTEND_IMAGE_TAG'
  export AWS_REGION='$AWS_REGION'

  # Authenticate to ECR via the instance profile, then verify both selected
  # tags exist before Compose changes a running service.
  aws ecr get-login-password --region "\$AWS_REGION" \
    | docker login --username AWS --password-stdin "\$REGISTRY"
  for pair in "madperfume-backend:\$IMAGE_TAG" "madperfume-frontend:\$FRONTEND_IMAGE_TAG"; do
    if ! aws ecr describe-images --repository-name "\${pair%%:*}" \
      --image-ids imageTag="\${pair#*:}" --region "\$AWS_REGION" >/dev/null 2>&1; then
      echo "Image '\$pair' was not found in ECR." >&2
      exit 1
    fi
  done

  COMPOSE="docker compose --env-file .env \
    -f deployment/compose/docker-compose.base.yml \
    -f deployment/compose/production/docker-compose.yml"

  \$COMPOSE pull
  \$COMPOSE up -d --force-recreate --remove-orphans

  echo "Mad Perfume rollback complete: backend=$BACKEND_TAG, frontend=$FRONTEND_IMAGE_TAG."
  \$COMPOSE ps
EOF
