# ─────────────────────────────────────────────────────────────
# School Application Variables — Dev
# ─────────────────────────────────────────────────────────────

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "dev"
}

variable "container_image" {
  description = "School Docker image URI"
  type        = string
  default     = "776735193826.dkr.ecr.us-east-1.amazonaws.com/mecandjeo-school-platform-dev:latest"
}

variable "container_port" {
  description = "School container port"
  type        = number
  default     = 8002
}

variable "task_cpu" {
  description = "ECS task CPU units"
  type        = number
  default     = 256
}

variable "task_memory" {
  description = "ECS task memory MB"
  type        = number
  default     = 512
}

variable "desired_count" {
  description = "Desired ECS task count"
  type        = number
  default     = 1
}

variable "health_check_path" {
  description = "ALB health check path"
  type        = string
  default     = "/health"
}

variable "min_capacity" {
  description = "Minimum ECS task count"
  type        = number
  default     = 1
}

variable "max_capacity" {
  description = "Maximum ECS task count"
  type        = number
  default     = 2
}

variable "scale_out_cpu_threshold" {
  description = "CPU threshold to scale out"
  type        = number
  default     = 70
}

variable "scale_in_cpu_threshold" {
  description = "CPU threshold to scale in"
  type        = number
  default     = 30
}