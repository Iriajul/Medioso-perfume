# ─── Global Variables ─────────────────────────────────────────────────
# These are shared across all Mad Perfume environments.
# Environment-specific values go in environments/<env>/terraform.tfvars

variable "project_name" {
  description = "Project name used for resource naming and tagging"
  type        = string
  default     = "madperfume"
}

variable "environment" {
  description = "Environment name (production, staging)"
  type        = string
}

variable "region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "aws_profile" {
  description = "AWS CLI profile name"
  type        = string
  default     = "default"
}

# ─── Compute ──────────────────────────────────────────────────────────

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.medium"
}

variable "ami" {
  description = "Optional explicit AMI ID. Leave empty to auto-select the latest Ubuntu 24.04 LTS via the aws_ami data source."
  type        = string
  default     = ""
}

variable "public_key_path" {
  description = "Path to SSH public key"
  type        = string
  default     = "~/.ssh/id_rsa.pub"
}

variable "root_volume_size" {
  description = "EC2 root EBS volume size in GB"
  type        = number
  default     = 30
}

# ─── Database ─────────────────────────────────────────────────────────

variable "db_username" {
  description = "RDS PostgreSQL username"
  type        = string
  # NO default — must be provided via tfvars or env
}

variable "db_password" {
  description = "RDS PostgreSQL password"
  type        = string
  sensitive   = true
  # NO default — must be provided via tfvars or env
}

variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.micro"
}

variable "db_allocated_storage" {
  description = "RDS allocated storage in GB"
  type        = number
  default     = 20
}

# ─── Storage ──────────────────────────────────────────────────────────

variable "bucket_name" {
  description = "S3 bucket name for media/static files"
  type        = string
}

# ─── Networking ───────────────────────────────────────────────────────

variable "allowed_ssh_cidrs" {
  description = "CIDR blocks allowed for SSH access (restrict to your IP!)"
  type        = list(string)
  default     = [] # Must be explicitly set
}

variable "domain" {
  description = "Primary domain name"
  type        = string
  default     = "bpmstudio.pt"
}

variable "host_prefix" {
  description = "Prefix for public hostnames, e.g. \"staging-\" gives staging-api.<domain>"
  type        = string
  default     = ""
}
