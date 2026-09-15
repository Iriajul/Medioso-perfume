# ─── Mad Perfume Bootstrap ──────────────────────────────────────────────
# Run this ONCE, before any environment. It creates the shared foundation:
#   1. S3 bucket that stores Terraform remote state for every environment
#   2. DynamoDB table that provides state locking (prevents concurrent applies)
#   3. ECR repositories (one per service) for Docker images
#
# This stack uses LOCAL state (it has to — it's creating the remote backend).
# Keep its terraform.tfstate file; it is small and non-sensitive.

# ─── 1. Remote state bucket ───────────────────────────────────────────
resource "aws_s3_bucket" "tfstate" {
  bucket = var.state_bucket_name

  tags = {
    Name      = "${var.project_name}-tfstate"
    Project   = var.project_name
    ManagedBy = "terraform-bootstrap"
  }
}

resource "aws_s3_bucket_versioning" "tfstate" {
  bucket = aws_s3_bucket.tfstate.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "tfstate" {
  bucket = aws_s3_bucket.tfstate.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "tfstate" {
  bucket                  = aws_s3_bucket.tfstate.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# ─── 2. State lock table ──────────────────────────────────────────────
resource "aws_dynamodb_table" "tflock" {
  name         = "${var.project_name}-tflock"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }

  tags = {
    Name      = "${var.project_name}-tflock"
    Project   = var.project_name
    ManagedBy = "terraform-bootstrap"
  }
}

# ─── 3. ECR repositories ──────────────────────────────────────────────
resource "aws_ecr_repository" "service" {
  for_each = toset(var.ecr_repositories)

  name                 = each.value
  image_tag_mutability = "MUTABLE" # allows reusing :latest / :staging tags

  image_scanning_configuration {
    scan_on_push = true # free vulnerability scan on each push
  }

  tags = {
    Name      = each.value
    Project   = var.project_name
    ManagedBy = "terraform-bootstrap"
  }
}

# Expire old/untagged images so the registry doesn't grow forever.
resource "aws_ecr_lifecycle_policy" "service" {
  for_each   = aws_ecr_repository.service
  repository = each.value.name

  policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Expire untagged images after 14 days"
        selection = {
          tagStatus   = "untagged"
          countType   = "sinceImagePushed"
          countUnit   = "days"
          countNumber = 14
        }
        action = { type = "expire" }
      },
      {
        rulePriority = 2
        description  = "Keep only the 20 most recent images (covers SHA tags)"
        selection = {
          tagStatus   = "any"
          countType   = "imageCountMoreThan"
          countNumber = 20
        }
        action = { type = "expire" }
      }
    ]
  })
}
