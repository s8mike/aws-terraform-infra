# ─────────────────────────────────────────────────────────────
# Portfolio Application Variables — Dev
# Shared infrastructure values (VPC, security groups, IAM)
# Since we are using the dashboard state via terraform_remote_state to read these values automatically, 
# they should not be required variables anymore — 
# the main.tf reads them directly from the remote state via locals.
# ─────────────────────────────────────────────────────────────

variable "aws_region" {
  description = "AWS region"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}

# ── Portfolio Application ─────────────────────────────────────
variable "portfolio_image" {
  description = "Docker image for the portfolio application"
  type        = string
  default     = "776735193826.dkr.ecr.us-east-1.amazonaws.com/mecandjeo-infra-portfolio:latest"
}

variable "portfolio_port" {
  description = "Port the portfolio container listens on"
  type        = number
  default     = 8001
}

variable "task_cpu" {
  description = "CPU units for the ECS task"
  type        = number
  default     = 256
}

variable "task_memory" {
  description = "Memory in MB for the ECS task"
  type        = number
  default     = 512
}

variable "desired_count" {
  description = "Desired number of ECS tasks"
  type        = number
  default     = 1
}

variable "min_capacity" {
  description = "Minimum number of ECS tasks"
  type        = number
  default     = 1
}

variable "max_capacity" {
  description = "Maximum number of ECS tasks"
  type        = number
  default     = 3
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