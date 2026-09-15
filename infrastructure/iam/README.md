# Deployer IAM Policies (`madperfumeapp`)

These are the **least-privilege** customer-managed policies for the Terraform
deployer user `madperfumeapp`. They are managed **out-of-band via the AWS CLI**
(not Terraform) on purpose — `madperfumeapp` is the identity Terraform runs as,
so managing its own permissions in Terraform state risks a mid-apply lockout.

> Replace `<AWS_ACCOUNT_ID>` in the JSON files with your 12-digit account ID,
> and set `madperfumeapp` to your actual deployer IAM username, before applying.

| Policy | ARN | Purpose |
|---|---|---|
| `MadPerfume-TerraformInfra` | `arn:aws:iam::<AWS_ACCOUNT_ID>:policy/MadPerfume-TerraformInfra` | ec2/rds/ecr/s3/dynamodb/kms — region-locked to `us-east-1` + scoped to our buckets/table/repos |
| `MadPerfume-TerraformIAM` | `arn:aws:iam::<AWS_ACCOUNT_ID>:policy/MadPerfume-TerraformIAM` | IAM writes scoped to `madperfume-*` roles/instance-profiles/policies + the GitHub OIDC provider; `PassRole` only the EC2 role. Read-only IAM elsewhere. **No privilege escalation.** |

Note the policies are named `MadPerfume-*` (capitalized) so they fall **outside** the
`policy/madperfume-*` self-manage scope — `madperfumeapp` cannot widen its own grants;
only an admin/root can edit these (separation of duties).

## Apply / update (run as an admin or root, not as madperfumeapp after hardening)
```bash
# create
aws iam create-policy --policy-name MadPerfume-TerraformInfra --policy-document file://MadPerfume-TerraformInfra.json
# update (new default version)
aws iam create-policy-version --policy-arn arn:aws:iam::<AWS_ACCOUNT_ID>:policy/MadPerfume-TerraformInfra \
  --policy-document file://MadPerfume-TerraformInfra.json --set-as-default
```

## Rollback (re-grant broad access if ever locked out)
```bash
for p in IAMFullAccess AmazonEC2FullAccess AmazonRDSFullAccess AmazonS3FullAccess \
         AmazonDynamoDBFullAccess AmazonEC2ContainerRegistryFullAccess; do
  aws iam attach-user-policy --user-name madperfumeapp --policy-arn arn:aws:iam::aws:policy/$p
done
```
Root account is the ultimate break-glass (console).
