# ─────────────────────────────────────────────────────────────
# Shared Infrastructure — Dev
# State key: mecandjeo-shared/dev/terraform.tfstate
#
# Contains ONLY free AWS resources:
#   VPC, subnets, IGW, route tables
#   Security groups (EC2, ALB, ECS)
#   IAM roles and policies
#   EC2 instance
#
# Deploy once — leave running permanently — ZERO COST
# All applications read outputs via terraform_remote_state
#
# App ports managed here — add new app port to app_ports list
# Current apps:
#   8000 — dashboard
#   8001 — portfolio
#   8002 — school
# ─────────────────────────────────────────────────────────────

module "vpc" {
  source = "../../../modules/vpc"

  vpc_cidr             = var.vpc_cidr
  project_name         = var.project_name
  environment          = var.environment
  public_subnet_cidrs  = var.public_subnet_cidrs
  private_subnet_cidrs = var.private_subnet_cidrs
  availability_zones   = var.availability_zones
}

module "security" {
  source = "../../../modules/security"

  project_name     = var.project_name
  environment      = var.environment
  vpc_id           = module.vpc.vpc_id
  allowed_ssh_cidr = var.allowed_ssh_cidr
}

module "compute" {
  source = "../../../modules/compute"

  project_name      = var.project_name
  environment       = var.environment
  public_subnet_id  = module.vpc.public_subnet_ids[0]
  security_group_id = module.security.ec2_security_group_id
  instance_type     = var.instance_type
  public_key        = var.public_key
}

# ─────────────────────────────────────────────────────────────
# Shared Infrastructure Outputs
# Consumed by all applications via terraform_remote_state
# ─────────────────────────────────────────────────────────────
output "vpc_id" {
  description = "VPC ID"
  value       = module.vpc.vpc_id
}

output "public_subnet_ids" {
  description = "Public subnet IDs"
  value       = module.vpc.public_subnet_ids
}

output "private_subnet_ids" {
  description = "Private subnet IDs"
  value       = module.vpc.private_subnet_ids
}

output "alb_security_group_id" {
  description = "ALB security group ID"
  value       = module.security.alb_security_group_id
}

output "ecs_security_group_id" {
  description = "ECS security group ID"
  value       = module.security.ecs_security_group_id
}

output "ecs_task_execution_role_arn" {
  description = "ECS task execution role ARN"
  value       = module.security.ecs_task_execution_role_arn
}

output "ecs_task_role_arn" {
  description = "ECS task role ARN — consumed by app states"
  value       = module.security.ecs_task_role_arn
}

output "ec2_instance_id" {
  description = "EC2 instance ID"
  value       = module.compute.instance_id
}

output "ec2_public_ip" {
  description = "EC2 public IP"
  value       = module.compute.public_ip
}