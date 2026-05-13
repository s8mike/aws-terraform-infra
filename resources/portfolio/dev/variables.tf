# ─────────────────────────────────────────────────────────────
# Portfolio Application Variables — Dev
# ─────────────────────────────────────────────────────────────

variable "aws_region" {
  description = "AWS region"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}

# ── Shared Infrastructure Inputs ─────────────────────────────
# These values come from the dashboard state via remote_state
# or are passed directly as variables
variable "vpc_id" {
  description = "VPC ID from shared infrastructure"
  type        = string
}

variable "public_subnet_ids" {
  description = "Public subnet IDs from shared infrastructure"
  type        = list(string)
}

variable "alb_security_group_id" {
  description = "ALB security group ID from shared infrastructure"
  type        = string
}

variable "ecs_security_group_id" {
  description = "ECS security group ID from shared infrastructure"
  type        = string
}

variable "ecs_task_execution_role_arn" {
  description = "ECS task execution role ARN from shared infrastructure"
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