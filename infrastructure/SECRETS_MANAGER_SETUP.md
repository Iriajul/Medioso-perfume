# Secrets for Mad Perfume

Nothing secret is committed to git. There are two places secrets live:

| Secret | Where | Consumed by |
|---|---|---|
| App config (`SECRET_KEY`, `DATABASE_URL`, superuser, S3 bucket…) | `deployment/environments/.env.<env>.backend` / `.frontend` on the operator machine (gitignored), copied to the server by Ansible with mode `0600` | backend / frontend containers |
| Grafana admin password | AWS Secrets Manager: `madperfume/<env>/grafana-password` | monitoring role (Ansible) via the EC2 instance role |
| Terraform DB credentials | `infrastructure/terraform/environments/<env>/terraform.tfvars` (gitignored) | RDS |
| CI → AWS | GitHub OIDC role (no static keys); only `AWS_ROLE_ARN` is stored as a GitHub secret | GitHub Actions |

## Create the Grafana secret (once per environment)

```bash
ENV=production   # or staging
aws secretsmanager create-secret \
  --name "madperfume/${ENV}/grafana-password" \
  --secret-string "$(openssl rand -base64 24)" \
  --region us-east-1 \
  --tags Key=Environment,Value=${ENV} Key=Project,Value=madperfume
```

The EC2 role (`infrastructure/terraform/shared/iam.tf`) can read only
`madperfume/<its env>/grafana-password-*`.

## Rotate

```bash
aws secretsmanager update-secret --secret-id "madperfume/${ENV}/grafana-password" \
  --secret-string "$(openssl rand -base64 24)" --region us-east-1
make ansible-prod   # re-runs the monitoring role with the new value
```

For app secrets: edit the local `.env.<env>.backend`, then `make ansible-prod`
(or `make ansible-staging`) to copy it and restart the stack.
