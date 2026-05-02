# ─────────────────────────────────────────────────────────────
# Production Environment Variables
# mecandjeo-infra — Mecandjeo Technology
# ─────────────────────────────────────────────────────────────

# General
variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
}

variable "project_name" {
  description = "Project name prefix for all resources"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}

# VPC
variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
}

variable "public_subnet_cidrs" {
  description = "List of CIDR blocks for public subnets"
  type        = list(string)
}

variable "private_subnet_cidrs" {
  description = "List of CIDR blocks for private subnets"
  type        = list(string)
}

variable "availability_zones" {
  description = "List of availability zones"
  type        = list(string)
}

# Compute
variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.small"
}

variable "allowed_ssh_cidr" {
  description = "Trusted IP CIDR allowed to SSH"
  type        = string
}

variable "public_key" {
  description = "SSH public key content for EC2 key pair"
  type        = string
}

# ECS
variable "container_image" {
  description = "Docker image to run in ECS"
  type        = string
  default     = "776735193826.dkr.ecr.us-east-1.amazonaws.com/mecandjeo-infra-prod:latest"
}

variable "container_port" {
  description = "Port the container listens on"
  type        = number
  default     = 8000
}

variable "task_cpu" {
  description = "CPU units for the ECS task"
  type        = number
  default     = 512
}

variable "task_memory" {
  description = "Memory in MB for the ECS task"
  type        = number
  default     = 1024
}

variable "desired_count" {
  description = "Desired number of ECS tasks"
  type        = number
  default     = 2
}

variable "health_check_path" {
  description = "Path for ALB health checks"
  type        = string
  default     = "/health"
}

variable "app_version" {
  description = "Application version"
  type        = string
  default     = "1.0.0"
}

# Auto Scaling
variable "min_capacity" {
  description = "Minimum number of ECS tasks"
  type        = number
  default     = 2
}

variable "max_capacity" {
  description = "Maximum number of ECS tasks"
  type        = number
  default     = 10
}

variable "scale_out_cpu_threshold" {
  description = "CPU percentage that triggers scale out"
  type        = number
  default     = 70
}

variable "scale_in_cpu_threshold" {
  description = "CPU percentage that triggers scale in"
  type        = number
  default     = 30
}