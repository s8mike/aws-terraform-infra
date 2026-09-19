variable "project_name" {
  description = "Project name used for resource naming"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID where security groups will be created"
  type        = string
}

variable "allowed_ssh_cidr" {
  description = "Trusted IP CIDR allowed to SSH into EC2 instances"
  type        = string
}

variable "aws_region" {
  description = "AWS region used by the resources"
  type        = string
}

variable "secret_arns" {
  description = "Secrets Manager ARNs the ECS task execution role can access"
  type        = list(string)
  default     = []
}
