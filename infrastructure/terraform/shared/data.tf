# ─── Data Sources ─────────────────────────────────────────────────────
# Looks up the latest Ubuntu 24.04 LTS (Noble) AMI published by Canonical
# for the CURRENT region — so you never hardcode a region-specific AMI ID.

data "aws_caller_identity" "current" {}

data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical's official AWS account ID

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd*/ubuntu-noble-24.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}
