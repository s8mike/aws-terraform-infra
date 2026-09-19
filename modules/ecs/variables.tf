variable "project_name" {
  description = "Project name used for resource naming"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "aws_region" {
  description = "AWS region"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID where ECS tasks will be deployed"
  type        = string
}

variable "subnet_ids" {
  description = "Subnet IDs where ECS tasks will run"
  type        = list(string)
}

variable "assign_public_ip" {
  description = "Whether ECS tasks receive public IP addresses"
  type        = bool
  default     = true
}

variable "ecs_security_group_id" {
  description = "Security group ID for ECS tasks - provided by security module"
  type        = string
}

variable "ecs_task_execution_role_arn" {
  description = "IAM role ARN for ECS task execution - provided by security module"
  type        = string
}

variable "container_image" {
  description = "Docker image to run in the ECS task"
  type        = string
  default     = "nginx:latest"
}

variable "container_port" {
  description = "Port the container listens on"
  type        = number
  default     = 80
}

variable "task_cpu" {
  description = "CPU units for the ECS task (256 = 0.25 vCPU)"
  type        = number
  default     = 256
}

variable "task_memory" {
  description = "Memory in MB for the ECS task"
  type        = number
  default     = 512
}

variable "desired_count" {
  description = "Desired number of ECS tasks to run"
  type        = number
  default     = 2
}

# variable "public_subnet_ids" {
#   description = "List of public subnet IDs for ECS tasks"
#   type        = list(string)
# }

# Added so ECS tasks can be registered with the ALB target group created in the load balancer module. This allows the ALB to route traffic to the ECS tasks.
variable "target_group_arn" {
  description = "ARN of the ALB target group to register ECS tasks with"
  type        = string
}

## New application variables added

variable "app_environment" {
  description = "Application environment name passed to container"
  type        = string
  default     = "dev"
}

variable "app_project_name" {
  description = "Project name passed to container"
  type        = string
  default     = "mecandjeo-infra"
}

variable "app_version" {
  description = "Application version passed to container"
  type        = string
  default     = "1.0.0"
}

variable "database_url_secret_arn" {
  description = "Optional ARN of the Secrets Manager secret containing DATABASE_URL"
  type        = string
  default     = null
}

# This prevent partial configuration when both secrets are required. If one is provided, the other must also be provided.
variable "secret_key_secret_arn" {
  description = "Optional ARN of the Secrets Manager secret containing SECRET_KEY"
  type        = string
  default     = null
  # validation {
  #   condition = (
  #     (var.database_url_secret_arn == null && var.secret_key_secret_arn == null) ||
  #     (var.database_url_secret_arn != null && var.secret_key_secret_arn != null)
  #   )
  #   error_message = "Provide both database_url_secret_arn and secret_key_secret_arn, or leave both unset."
  # }
}

variable "log_retention_in_days" {
  description = "Number of days to retain ECS CloudWatch logs"
  type        = number
  default     = 365
}

variable "log_kms_key_id" {
  description = "Optional KMS key ARN or ID for encrypting ECS CloudWatch logs"
  type        = string
  default     = null
}