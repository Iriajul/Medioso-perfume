output "state_bucket" {
  value       = aws_s3_bucket.tfstate.bucket
  description = "S3 bucket holding Terraform remote state"
}

output "lock_table" {
  value       = aws_dynamodb_table.tflock.name
  description = "DynamoDB table used for state locking"
}

output "ecr_repository_urls" {
  value       = { for name, repo in aws_ecr_repository.service : name => repo.repository_url }
  description = "Map of service name -> ECR repository URL (use these in CI/compose)"
}
