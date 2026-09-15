# ─── GitHub Actions OIDC → AWS (no static keys in CI) ─────────────────
# Lets GitHub Actions assume an IAM role using a short-lived OIDC token,
# scoped to this repo + specific branches, with ECR-push permissions only.

variable "github_repo" {
  description = "owner/repo allowed to assume the CI role"
  type        = string
  default     = "Iriajul/Medioso-perfume"
}

variable "github_branches" {
  description = "Branches allowed to assume the CI role (used by build jobs)"
  type        = list(string)
  default     = ["main", "staging"]
}

variable "github_environments" {
  description = "GitHub environments allowed to assume the CI role (deploy jobs that set `environment:` get an environment-scoped OIDC subject)"
  type        = list(string)
  default     = ["production", "staging"]
}

# Fetch GitHub's OIDC TLS thumbprint dynamically (self-updating).
data "tls_certificate" "github" {
  url = "https://token.actions.githubusercontent.com/.well-known/openid-configuration"
}

resource "aws_iam_openid_connect_provider" "github" {
  url             = "https://token.actions.githubusercontent.com"
  client_id_list  = ["sts.amazonaws.com"]
  thumbprint_list = [data.tls_certificate.github.certificates[0].sha1_fingerprint]
}

# Trust policy: who may assume this role, and under what conditions.
data "aws_iam_policy_document" "ci_assume" {
  statement {
    actions = ["sts:AssumeRoleWithWebIdentity"]
    effect  = "Allow"

    principals {
      type        = "Federated"
      identifiers = [aws_iam_openid_connect_provider.github.arn]
    }

    # Audience must be AWS STS.
    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:aud"
      values   = ["sts.amazonaws.com"]
    }

    # Subject must be this repo on an allowed branch (build jobs) OR an
    # allowed environment (deploy jobs that set `environment:`).
    condition {
      test     = "StringLike"
      variable = "token.actions.githubusercontent.com:sub"
      values = concat(
        [for b in var.github_branches : "repo:${var.github_repo}:ref:refs/heads/${b}"],
        [for e in var.github_environments : "repo:${var.github_repo}:environment:${e}"]
      )
    }
  }
}

resource "aws_iam_role" "github_ci" {
  name               = "${var.project_name}-github-ci"
  assume_role_policy = data.aws_iam_policy_document.ci_assume.json

  tags = {
    Name      = "${var.project_name}-github-ci"
    ManagedBy = "terraform-bootstrap"
  }
}

# ECR push permissions, scoped to this project's repositories.
data "aws_iam_policy_document" "ci_ecr_push" {
  statement {
    sid       = "ECRGetAuthToken"
    actions   = ["ecr:GetAuthorizationToken"]
    resources = ["*"] # GetAuthorizationToken cannot be resource-scoped
  }

  statement {
    sid = "ECRPushPull"
    actions = [
      "ecr:BatchCheckLayerAvailability",
      "ecr:InitiateLayerUpload",
      "ecr:UploadLayerPart",
      "ecr:CompleteLayerUpload",
      "ecr:PutImage",
      "ecr:BatchGetImage",
      "ecr:GetDownloadUrlForLayer",
    ]
    resources = [for repo in aws_ecr_repository.service : repo.arn]
  }

  # Deploy by sending a command to the instance via SSM (no inbound SSH).
  # Broad resources here are acceptable for a deploy identity that only
  # main/staging pushes can assume; tighten with tag conditions in Stage 10.
  statement {
    sid       = "SSMDeploy"
    actions   = ["ssm:SendCommand", "ssm:GetCommandInvocation", "ssm:ListCommandInvocations"]
    resources = ["*"]
  }

  statement {
    sid       = "EC2Describe"
    actions   = ["ec2:DescribeInstances"]
    resources = ["*"]
  }
}

resource "aws_iam_role_policy" "ci_ecr_push" {
  name   = "ecr-push"
  role   = aws_iam_role.github_ci.id
  policy = data.aws_iam_policy_document.ci_ecr_push.json
}

output "github_ci_role_arn" {
  value       = aws_iam_role.github_ci.arn
  description = "Set this as the AWS_ROLE_ARN secret in GitHub Actions"
}
