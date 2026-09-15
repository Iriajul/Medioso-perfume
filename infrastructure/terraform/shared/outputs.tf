output "ec2_public_ip" {
  value       = aws_eip.static_ip.public_ip
  description = "Elastic IP address of the Mad Perfume EC2 instance"
}

output "s3_bucket_name" {
  value       = aws_s3_bucket.media.bucket
  description = "S3 bucket name"
}

output "rds_endpoint" {
  value       = aws_db_instance.postgres.endpoint
  description = "RDS instance endpoint"
  sensitive   = true
}

output "rds_username" {
  value       = aws_db_instance.postgres.username
  description = "RDS username"
  sensitive   = true
}

output "security_group_id" {
  value       = aws_security_group.app_sg.id
  description = "Application security group ID"
}
