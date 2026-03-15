# Stage 2 onwards: module calls will live here
# For now this declares the variables this environment needs

variable "aws_region" {
  description = "AWS region"
  type        = string
}

# variable "project_name" {
#   description = "Project name prefix"
#   type        = string
# }

# variable "environment" {
#   description = "Environment name"
#   type        = string
# }

module "vpc" {
  source               = "../../modules/vpc"
  aws_region           = var.aws_region
  vpc_cidr             = var.vpc_cidr
  project_name         = var.project_name
  environment          = var.environment
  public_subnet_cidrs  = var.public_subnet_cidrs
  private_subnet_cidrs = var.private_subnet_cidrs
  availability_zones   = var.availability_zones
}