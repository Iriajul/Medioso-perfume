#!/bin/bash
# ─── terraform-apply.sh ───────────────────────────────────────────────
# Safely apply Terraform for a given Mad Perfume environment.
# Usage: ./terraform-apply.sh [production|staging]
set -euo pipefail

ENV="${1:-staging}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TF_DIR="$(dirname "$SCRIPT_DIR")/../infrastructure/terraform/environments/$ENV"

if [[ ! -d "$TF_DIR" ]]; then
  echo "Error: environment directory not found: $TF_DIR"
  exit 1
fi

echo "▶ Terraform Init ($ENV)"
cd "$TF_DIR"
if [[ ! -f backend.hcl ]]; then
  echo "Error: backend.hcl not found in $TF_DIR"
  echo "       Copy backend.hcl.example → backend.hcl and set your state bucket first."
  exit 1
fi
terraform init -backend-config=backend.hcl

echo "▶ Terraform Validate"
terraform validate

echo "▶ Terraform Plan"
terraform plan -out=tfplan

if [[ "$ENV" == "production" ]]; then
  echo ""
  read -p "⚠️  Apply to PRODUCTION? Type 'yes' to confirm: " confirm
  if [[ "$confirm" != "yes" ]]; then
    echo "Aborted."
    exit 0
  fi
fi

echo "▶ Terraform Apply"
terraform apply "tfplan"
rm -f tfplan

echo "✓ Terraform apply complete for Mad Perfume $ENV"
