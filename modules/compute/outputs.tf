output "instance_id" {
  description = "EC2 instance ID"
  value       = aws_instance.main.id
}

output "public_ip" {
  description = "Public IP address of the EC2 instance"
  value       = aws_instance.main.public_ip
}

output "security_group_id" {
  description = "Security group ID of the EC2 instance"
  value       = aws_security_group.ec2.id
}