# Remote state in S3 + DynamoDB locking. Supplied at init time via:
#   terraform init -backend-config=backend.hcl
terraform {
  backend "s3" {}
}
