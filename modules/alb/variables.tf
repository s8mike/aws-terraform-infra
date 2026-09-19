variable "project_name" {
  description = "Project name used for resource naming"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID where the ALB will be deployed"
  type        = string
}

variable "public_subnet_ids" {
  description = "List of public subnet IDs for the ALB"
  type        = list(string)
}

variable "alb_security_group_id" {
  description = "Security group ID for the ALB"
  type        = string
}

variable "container_port" {
  description = "Port the container listens on"
  type        = number
  default     = 80
}

variable "health_check_path" {
  description = "Path for ALB health checks"
  type        = string
  default     = "/"
}

variable "enable_deletion_protection" {
  description = "Whether to enable deletion protection for the ALB"
  type        = bool
  default     = false
}

variable "access_logs_enabled" {
  description = "Whether to enable ALB access logging"
  type        = bool
  default     = false
}

variable "access_logs_bucket" {
  description = "Existing S3 bucket for ALB access logs"
  type        = string
  default     = null
}

variable "access_logs_prefix" {
  description = "Optional prefix for ALB access logs in the S3 bucket"
  type        = string
  default     = null
}

variable "acm_certificate_arn" {
  description = "Optional ACM certificate ARN for the ALB HTTPS listener"
  type        = string
  default     = null
}

variable "https_enabled" {
  description = "Whether to create an HTTPS listener"
  type        = bool
  default     = false
}

variable "http_to_https_redirect" {
  description = "Whether HTTP traffic should redirect to HTTPS"
  type        = bool
  default     = false
}

variable "waf_web_acl_arn" {
  description = "Optional ARN of an existing AWS WAFv2 Web ACL to associate with the ALB"
  type        = string
  default     = null
}