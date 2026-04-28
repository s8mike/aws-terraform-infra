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

# New variables for application
variable "container_port" {
  description = "Port the container listens on"
  type        = number
  default     = 8000
}