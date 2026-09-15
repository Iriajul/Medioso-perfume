# ─── Mad Perfume Staging Environment ────────────────────────────────────
# Init:  terraform init -backend-config=backend.hcl
# Apply: terraform apply   (secrets come from terraform.tfvars / TF_VAR_*)

module "infra" {
  source = "../../shared"

  project_name = "madperfume"
  environment  = "staging"
  region       = "us-east-1"
  aws_profile  = "default"
  domain       = "bpmstudio.pt"
  host_prefix  = "staging-"

  # Compute — smaller for staging; latest Ubuntu 24.04 auto-selected.
  instance_type   = "t3.small"
  public_key_path = var.public_key_path

  # Database
  db_username          = var.db_username
  db_password          = var.db_password
  db_instance_class    = "db.t3.micro"
  db_allocated_storage = 10

  # Storage
  bucket_name = "madperfume-media-staging"

  # Networking — your IP(s), provided via terraform.tfvars (never committed)
  allowed_ssh_cidrs = var.allowed_ssh_cidrs
}

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

output "server_ip" {
  value = module.infra.ec2_public_ip
}
