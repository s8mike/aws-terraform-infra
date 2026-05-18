# ─────────────────────────────────────────────────────────────
# Dashboard Environment — Dev
# State key: mecandjeo-dashboard/dev/terraform.tfstate
# Contains: Shared infrastructure + Dashboard application
# ─────────────────────────────────────────────────────────────

module "vpc" {
  source = "../../modules/vpc"

  vpc_cidr             = var.vpc_cidr
  project_name         = var.project_name
  environment          = var.environment
  public_subnet_cidrs  = var.public_subnet_cidrs
  private_subnet_cidrs = var.private_subnet_cidrs
  availability_zones   = var.availability_zones
}

module "security" {
  source = "../../modules/security"

  project_name     = var.project_name
  environment      = var.environment
  vpc_id           = module.vpc.vpc_id
  allowed_ssh_cidr = var.allowed_ssh_cidr
  # container_port   = var.container_port - Not needed as ports are now fetched dynamically from the modules/security/main.tf outputs. 
  #This is because the security module is shared across multiple applications and we want to avoid hardcoding ports here.
}

module "compute" {
  source = "../../modules/compute"

  project_name      = var.project_name
  environment       = var.environment
  public_subnet_id  = module.vpc.public_subnet_ids[0]
  security_group_id = module.security.ec2_security_group_id
  instance_type     = var.instance_type
  public_key        = var.public_key
}

module "alb" {
  source = "../../modules/alb"

  project_name          = var.project_name
  environment           = var.environment
  vpc_id                = module.vpc.vpc_id
  public_subnet_ids     = module.vpc.public_subnet_ids
  alb_security_group_id = module.security.alb_security_group_id
  container_port        = var.container_port
  health_check_path     = var.health_check_path
}

module "ecs" {
  source = "../../modules/ecs"

  project_name                = var.project_name
  environment                 = var.environment
  aws_region                  = var.aws_region
  vpc_id                      = module.vpc.vpc_id
  public_subnet_ids           = module.vpc.public_subnet_ids
  ecs_security_group_id       = module.security.ecs_security_group_id
  ecs_task_execution_role_arn = module.security.ecs_task_execution_role_arn
  container_image             = var.container_image
  container_port              = var.container_port
  task_cpu                    = var.task_cpu
  task_memory                 = var.task_memory
  desired_count               = var.desired_count
  target_group_arn            = module.alb.target_group_arn
  app_environment             = var.environment
  app_project_name            = var.project_name
  app_version                 = "1.0.0"
}

module "autoscaling" {
  source = "../../modules/autoscaling"

  project_name            = var.project_name
  environment             = var.environment
  ecs_cluster_name        = module.ecs.ecs_cluster_name
  ecs_service_name        = module.ecs.ecs_service_name
  min_capacity            = var.min_capacity
  max_capacity            = var.max_capacity
  scale_out_cpu_threshold = var.scale_out_cpu_threshold
  scale_in_cpu_threshold  = var.scale_in_cpu_threshold
}

# ─────────────────────────────────────────────────────────────
# Outputs
# ─────────────────────────────────────────────────────────────
output "alb_dns_name" {
  description = "Dashboard ALB DNS name"
  value       = module.alb.alb_dns_name
}

output "ec2_public_ip" {
  description = "Public IP of the EC2 instance"
  value       = module.compute.public_ip
}

output "ec2_instance_id" {
  description = "EC2 instance ID"
  value       = module.compute.instance_id
}

output "ecs_cluster_name" {
  description = "ECS cluster name"
  value       = module.ecs.ecs_cluster_name
}

output "cloudwatch_log_group" {
  description = "CloudWatch log group for ECS"
  value       = module.ecs.cloudwatch_log_group_name
}


# ── Shared Infrastructure Outputs ────────────────────────────
# Consumed by portfolio and future applications via
# terraform_remote_state data source
output "vpc_id" {
  description = "VPC ID — consumed by app-specific states"
  value       = module.vpc.vpc_id
}

output "public_subnet_ids" {
  description = "Public subnet IDs — consumed by app-specific states"
  value       = module.vpc.public_subnet_ids
}

output "private_subnet_ids" {
  description = "Private subnet IDs — consumed by app-specific states"
  value       = module.vpc.private_subnet_ids
}

output "alb_security_group_id" {
  description = "ALB security group ID — consumed by app-specific states"
  value       = module.security.alb_security_group_id
}

output "ecs_security_group_id" {
  description = "ECS security group ID — consumed by app-specific states"
  value       = module.security.ecs_security_group_id
}

output "ecs_task_execution_role_arn" {
  description = "ECS task execution role ARN — consumed by app-specific states"
  value       = module.security.ecs_task_execution_role_arn
}







##============================================
## FIRST WORKING VERSION OF THE INFRASTRUCTURE
##=============================================

# module "vpc" {
#   source = "../../modules/vpc"

#   vpc_cidr             = var.vpc_cidr
#   project_name         = var.project_name
#   environment          = var.environment
#   public_subnet_cidrs  = var.public_subnet_cidrs
#   private_subnet_cidrs = var.private_subnet_cidrs
#   availability_zones   = var.availability_zones
# }

# module "security" {
#   source = "../../modules/security"

#   project_name     = var.project_name
#   environment      = var.environment
#   vpc_id           = module.vpc.vpc_id
#   allowed_ssh_cidr = var.allowed_ssh_cidr
#   container_port   = var.container_port
# }

# module "compute" {
#   source = "../../modules/compute"

#   project_name      = var.project_name
#   environment       = var.environment
#   public_subnet_id  = module.vpc.public_subnet_ids[0]
#   security_group_id = module.security.ec2_security_group_id
#   instance_type     = var.instance_type
#   public_key        = var.public_key
# }

# module "alb" {
#   source = "../../modules/alb"

#   project_name          = var.project_name
#   environment           = var.environment
#   vpc_id                = module.vpc.vpc_id
#   public_subnet_ids     = module.vpc.public_subnet_ids
#   alb_security_group_id = module.security.alb_security_group_id
#   container_port        = var.container_port
#   health_check_path     = var.health_check_path
# }

# module "ecs" {
#   source = "../../modules/ecs"

#   project_name                = var.project_name
#   environment                 = var.environment
#   aws_region                  = var.aws_region
#   vpc_id                      = module.vpc.vpc_id
#   public_subnet_ids           = module.vpc.public_subnet_ids
#   ecs_security_group_id       = module.security.ecs_security_group_id
#   ecs_task_execution_role_arn = module.security.ecs_task_execution_role_arn
#   container_image             = var.container_image
#   container_port              = var.container_port
#   task_cpu                    = var.task_cpu
#   task_memory                 = var.task_memory
#   desired_count               = var.desired_count
#   target_group_arn            = module.alb.target_group_arn

#   # New — runtime environment variables for the application
#   app_environment  = var.environment
#   app_project_name = var.project_name
#   app_version      = "1.0.0"
# }

# # Auto Scaling Module stage 7
# ## The remote state module will be activated when we set up S3 remote state. We will then pull the S3 bucket and DynamoDB table names from the remote state outputs and pass them to the
# # module "remote_state" {
# #   source = "../../modules/remote-state"

# #   project_name = var.project_name
# #   environment  = var.environment
# #   aws_region   = var.aws_region
# # }

# module "autoscaling" {
#   source = "../../modules/autoscaling"

#   project_name            = var.project_name
#   environment             = var.environment
#   ecs_cluster_name        = module.ecs.ecs_cluster_name
#   ecs_service_name        = module.ecs.ecs_service_name
#   min_capacity            = var.min_capacity
#   max_capacity            = var.max_capacity
#   scale_out_cpu_threshold = var.scale_out_cpu_threshold
#   scale_in_cpu_threshold  = var.scale_in_cpu_threshold
# }

# #===========================================================
# # Second Application to create using this infrastructure.
# #===========================================================
# # ── App 2 — Portfolio ─────────────────────────────────────────
# module "alb_portfolio" {
#   source = "../../modules/alb"

#   project_name          = "mecandjeo-portfolio"
#   environment           = var.environment
#   vpc_id                = module.vpc.vpc_id
#   public_subnet_ids     = module.vpc.public_subnet_ids
#   alb_security_group_id = module.security.alb_security_group_id
#   container_port        = var.portfolio_port
#   health_check_path     = "/health"
# }

# module "ecs_portfolio" {
#   source = "../../modules/ecs"

#   project_name                = "mecandjeo-portfolio"
#   environment                 = var.environment
#   aws_region                  = var.aws_region
#   vpc_id                      = module.vpc.vpc_id
#   public_subnet_ids           = module.vpc.public_subnet_ids
#   ecs_security_group_id       = module.security.ecs_security_group_id
#   ecs_task_execution_role_arn = module.security.ecs_task_execution_role_arn
#   container_image             = var.portfolio_image
#   container_port              = var.portfolio_port
#   task_cpu                    = 256
#   task_memory                 = 512
#   desired_count               = 1
#   target_group_arn            = module.alb_portfolio.target_group_arn
#   app_environment             = var.environment
#   app_project_name            = "mecandjeo-portfolio"
#   app_version                 = "1.0.0"
# }

# module "autoscaling_portfolio" {
#   source = "../../modules/autoscaling"

#   project_name            = "mecandjeo-portfolio"
#   environment             = var.environment
#   ecs_cluster_name        = module.ecs_portfolio.ecs_cluster_name
#   ecs_service_name        = module.ecs_portfolio.ecs_service_name
#   min_capacity            = 1
#   max_capacity            = 3
#   scale_out_cpu_threshold = 70
#   scale_in_cpu_threshold  = 30
# }


# #===========================================================
# # Outputs for the infrastructure and applications
# #===========================================================
# output "alb_dns_name" {
#   description = "ALB DNS name - open this in your browser"
#   value       = module.alb.alb_dns_name
# }

# output "ec2_public_ip" {
#   description = "Public IP of the EC2 instance"
#   value       = module.compute.public_ip
# }

# output "ec2_instance_id" {
#   description = "EC2 instance ID"
#   value       = module.compute.instance_id
# }

# output "ecs_cluster_name" {
#   description = "ECS cluster name"
#   value       = module.ecs.ecs_cluster_name
# }

# # Removed — ECR managed outside Terraform. This will uncommented later when we add ECR back.
# # output "ecr_repository_url" {
# #   description = "ECR repository URL"
# #   value       = module.ecs.ecr_repository_url
# # }

# output "cloudwatch_log_group" {
#   description = "CloudWatch log group for ECS"
#   value       = module.ecs.cloudwatch_log_group_name
# }

# ## Below remote state outputs will be activated when we set up s3 remote state.

# # output "s3_state_bucket" {
# #   description = "S3 bucket storing Terraform state"
# #   value       = module.remote_state.s3_bucket_name
# # }

# # output "dynamodb_lock_table" {
# #   description = "DynamoDB table for state locking"
# #   value       = module.remote_state.dynamodb_table_name
# # }
# #===========================================================
# # New outputs for the portfolio application
# output "portfolio_alb_dns_name" {
#   description = "Portfolio ALB DNS name — open in browser"
#   value       = module.alb_portfolio.alb_dns_name
# }
# #============================================================