# Phase 9: MHC application environment variables.
variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "project_name" {
  type    = string
  default = "mecandjeo-mhc-monitoring"
}

variable "environment" {
  type    = string
  default = "dev"
}

variable "container_image" {
  description = "Immutable MHC API image URI supplied by the deployment pipeline"
  type        = string
  default     = "public.ecr.aws/docker/library/python:3.12-slim"
}

variable "container_port" {
  type    = number
  default = 8004
}

variable "task_cpu" {
  type    = number
  default = 256
}

variable "task_memory" {
  type    = number
  default = 512
}

variable "desired_count" {
  type    = number
  default = 1
}

variable "min_capacity" {
  type    = number
  default = 1
}

variable "max_capacity" {
  type    = number
  default = 2
}

variable "database_url_secret_arn" {
  description = "Secrets Manager ARN containing DATABASE_URL; set by secure CI/CD variables"
  type        = string
  default     = null
}

variable "secret_key_secret_arn" {
  description = "Secrets Manager ARN containing SECRET_KEY; set by secure CI/CD variables"
  type        = string
  default     = null
}

variable "rds_instance_class" {
  type    = string
  default = "db.t3.micro"
}

variable "rds_deletion_protection" {
  type    = bool
  default = false
}
