variable "project_name" {
  description = "Project name used for resource naming"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "ecs_cluster_name" {
  description = "ECS cluster name to attach auto scaling to"
  type        = string
}

variable "ecs_service_name" {
  description = "ECS service name to scale"
  type        = string
}

variable "min_capacity" {
  description = "Minimum number of ECS tasks"
  type        = number
  default     = 2
}

variable "max_capacity" {
  description = "Maximum number of ECS tasks"
  type        = number
  default     = 6
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