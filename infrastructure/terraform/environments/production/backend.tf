# Remote state in S3 + DynamoDB locking. The actual values are supplied at
# init time via:  terraform init -backend-config=backend.hcl
terraform {
  backend "s3" {}
}
