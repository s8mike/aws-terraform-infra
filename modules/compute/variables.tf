variable "project_name" {
  description = "Project name used for resource naming"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "public_subnet_id" {
  description = "Public subnet ID to launch the EC2 instance in"
  type        = string
}

variable "security_group_id" {
  description = "Security group ID for the EC2 instance - provided by security module"
  type        = string
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.micro"
}

variable "public_key" {
  description = "SSH public key content for EC2 key pair"
  type        = string
}

# This variable is commented out because at the later stage because od data source will be used to fetch the latest Amazon Linux 2 AMI ID, so it is not needed to be provided as an input variable.
# variable "ami_id" {
#   description = "AMI ID for the EC2 instance"
#   type        = string
# }