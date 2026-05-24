# ─────────────────────────────────────────────────────────────
# Shared Infrastructure Variables — Dev
# Contains: VPC, security groups, IAM, EC2
# These resources are FREE — deploy once, leave running
# All applications read these outputs via terraform_remote_state
# ─────────────────────────────────────────────────────────────

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name prefix for all shared resources"
  type        = string
  default     = "mecandjeo-infra"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "dev"
}

# ── VPC ───────────────────────────────────────────────────────
variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for public subnets"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "private_subnet_cidrs" {
  description = "CIDR blocks for private subnets"
  type        = list(string)
  default     = ["10.0.3.0/24", "10.0.4.0/24"]
}

variable "availability_zones" {
  description = "Availability zones"
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b"]
}

# ── Compute ───────────────────────────────────────────────────
variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.micro"
}

variable "allowed_ssh_cidr" {
  description = "Trusted IP CIDR allowed to SSH"
  type        = string
}

variable "public_key" {
  description = "SSH public key content for EC2 key pair"
  type        = string
}