#!/bin/bash
# ─── deploy.sh ────────────────────────────────────────────────────────
# BOOTSTRAP a Mad Perfume environment from scratch: Terraform (AWS infra) →
# Ansible (install Docker/Nginx/SSL, ship compose + env files, first "up").
# Usage: ./deploy.sh [production|staging]
#
# Division of responsibility (all paths share ONE compose invocation:
# base + per-env override, so behaviour is identical everywhere):
#   • Terraform        → provisions AWS infra (EC2/RDS/S3).      [this script]
#   • Ansible          → bootstraps the server + first deploy.   [this script]
#   • GitHub Actions   → ongoing deploys on every push to main.  (.github/workflows)
#   • rollback.sh      → same compose, re-pinned to a prior tag.
set -euo pipefail

ENV="${1:-production}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEPLOY_DIR="$(dirname "$SCRIPT_DIR")"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Mad Perfume — Deploying to: $ENV"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [[ "$ENV" != "production" && "$ENV" != "staging" ]]; then
  echo "Error: environment must be 'production' or 'staging'"
  exit 1
fi

# Step 1: Provision infrastructure (if needed)
echo ""
echo "▶ Step 1: Terraform apply ($ENV)"
cd "$DEPLOY_DIR/../infrastructure/terraform/environments/$ENV"
terraform init -backend-config=backend.hcl
terraform apply -auto-approve

# Step 2: Configure server
echo ""
echo "▶ Step 2: Ansible configure ($ENV)"
cd "$DEPLOY_DIR/../infrastructure/ansible"
ansible-playbook \
  -i "inventories/$ENV/hosts" \
  -e "env=$ENV" \
  playbooks/site.yml

echo ""
echo "✓ Mad Perfume deployment to $ENV complete!"
