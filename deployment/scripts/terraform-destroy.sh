#!/bin/bash
# ─── terraform-destroy.sh ─────────────────────────────────────────────
# Destroy Terraform-managed Mad Perfume infrastructure.
# Usage: ./terraform-destroy.sh [production|staging]
set -euo pipefail

ENV="${1:-staging}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TF_DIR="$(dirname "$SCRIPT_DIR")/../infrastructure/terraform/environments/$ENV"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ⚠️  DESTROYING Mad Perfume infrastructure: $ENV"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

read -p "Type the environment name to confirm ('$ENV'): " confirm
if [[ "$confirm" != "$ENV" ]]; then
  echo "Aborted."
  exit 0
fi

cd "$TF_DIR"
terraform init
terraform destroy -auto-approve

echo "✓ Mad Perfume infrastructure for $ENV has been destroyed."
