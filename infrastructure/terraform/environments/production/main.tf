# ─── Mad Perfume Production Environment ─────────────────────────────────
# Init:  terraform init -backend-config=backend.hcl
# Apply: terraform apply   (secrets come from terraform.tfvars / TF_VAR_*)

module "infra" {
  source = "../../shared"

  project_name = "madperfume"
  environment  = "production"
  region       = "us-east-1"
  aws_profile  = "madperfume"
  domain       = "bpmstudio.pt"

  # Compute — `ami` left unset → latest Ubuntu 24.04 LTS auto-selected.
  instance_type   = "t3.medium"
  public_key_path = var.public_key_path

  # Database
  db_username          = var.db_username
  db_password          = var.db_password
  db_instance_class    = "db.t3.micro"
  db_allocated_storage = 20

  # Storage
  bucket_name = "madperfume-media-prod"

  # Networking — your IP(s), provided via terraform.tfvars (never committed)
  allowed_ssh_cidrs = var.allowed_ssh_cidrs
}

# ─── Secrets / per-operator values (set in terraform.tfvars) ──────────
variable "db_username" {
  type      = string
  sensitive = true
}

variable "db_password" {
  type      = string
  sensitive = true
}

variable "allowed_ssh_cidrs" {
  description = "CIDRs allowed to SSH, e.g. [\"1.2.3.4/32\"]"
  type        = list(string)
}

variable "public_key_path" {
  description = "Path to your SSH public key"
  type        = string
  default     = "~/.ssh/id_rsa.pub"
}

# ─── Outputs ──────────────────────────────────────────────────────────
output "server_ip" {
  value = module.infra.ec2_public_ip
}

output "rds_endpoint" {
  value     = module.infra.rds_endpoint
  sensitive = true
}
