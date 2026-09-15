# Deployment Checklist (first-time setup)

All AWS commands use the `default` profile in `us-east-1`.

## 1. Bootstrap (once)
```bash
cd infrastructure/terraform/bootstrap
cp terraform.tfvars.example terraform.tfvars   # set a globally-unique state_bucket_name
# ci.tf: github_repo is already set to Iriajul/Medioso-perfume
terraform init && terraform apply
```
Outputs: state bucket, lock table, ECR repos (`madperfume-backend`, `madperfume-frontend`),
`github_ci_role_arn`.

## 2. GitHub repository
- Secret `AWS_ROLE_ARN` = `github_ci_role_arn` output
- Environments: `production`, `staging` (add required reviewers on production if wanted)
- Optional variables: `PRODUCTION_API_URL`, `STAGING_API_URL`

## 3. Environment infrastructure
```bash
cd infrastructure/terraform/environments/<env>
cp backend.hcl.example backend.hcl            # set bucket from step 1
cp terraform.tfvars.example terraform.tfvars  # DB creds, your IP, SSH key
make tf-apply ENV=<env>
```
Note the `server_ip` output.

## 4. DNS (Hostinger → bpmstudio.pt → DNS)
Add A records pointing to `server_ip`:
- production: `api`, `admin`
- staging: `staging-api`, `staging-admin`

Wait until `dig +short api.bpmstudio.pt` returns the IP (certbot needs it).

## 5. Server configuration
```bash
# put server_ip in infrastructure/ansible/inventories/<env>/hosts
cp deployment/environments/.env.<env>.backend.example  deployment/environments/.env.<env>.backend
cp deployment/environments/.env.<env>.frontend.example deployment/environments/.env.<env>.frontend
# fill in SECRET_KEY, DATABASE_URL (RDS endpoint, ?sslmode=require), bucket, superuser
# create the Grafana secret — see infrastructure/SECRETS_MANAGER_SETUP.md
REGISTRY=<acct>.dkr.ecr.us-east-1.amazonaws.com make ansible-prod   # or ansible-staging
```

## 6. Deploy
Push to `staging` / `main`. CI builds both images, pushes to ECR and runs
`server-deploy.sh` on the instance via SSM.

Rollback: `REGISTRY=... EC2_HOST=... make rollback TAG=<sha> [FRONTEND_TAG=<sha>]`
