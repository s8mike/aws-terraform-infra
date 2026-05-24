# ─────────────────────────────────────────────────────────────
# Portfolio Application — Dev
# State key: mecandjeo-portfolio/dev/terraform.tfstate
#
# This configuration deploys only the portfolio application.
# Shared infrastructure (VPC, security groups, IAM) is managed
# by the dashboard state and consumed here via remote_state.
# ─────────────────────────────────────────────────────────────

# ── Read Shared Infrastructure Outputs ───────────────────────
# From:
# data "terraform_remote_state" "dashboard" {
#   backend = "s3"
#   config = {
#     bucket = "mecandjeo-infra-dev-tfstate"
#     key    = "mecandjeo-dashboard/dev/terraform.tfstate"
#     region = "us-east-1"
#   }
# }

# locals {
#   vpc_id                      = data.terraform_remote_state.dashboard.outputs.vpc_id
#   public_subnet_ids           = data.terraform_remote_state.dashboard.outputs.public_subnet_ids
#   alb_security_group_id       = data.terraform_remote_state.dashboard.outputs.alb_security_group_id
#   ecs_security_group_id       = data.terraform_remote_state.dashboard.outputs.ecs_security_group_id
#   ecs_task_execution_role_arn = data.terraform_remote_state.dashboard.outputs.ecs_task_execution_role_arn
# }

# Change TO:
data "terraform_remote_state" "shared" {
  backend = "s3"
  config = {
    bucket = "mecandjeo-infra-dev-tfstate"
    key    = "mecandjeo-shared/dev/terraform.tfstate"
    region = "us-east-1"
  }
}

locals {
  vpc_id                      = data.terraform_remote_state.shared.outputs.vpc_id
  public_subnet_ids           = data.terraform_remote_state.shared.outputs.public_subnet_ids
  alb_security_group_id       = data.terraform_remote_state.shared.outputs.alb_security_group_id
  ecs_security_group_id       = data.terraform_remote_state.shared.outputs.ecs_security_group_id
  ecs_task_execution_role_arn = data.terraform_remote_state.shared.outputs.ecs_task_execution_role_arn
}



# Portfolio-specific variables in addition to shared ones

# ── Portfolio ALB ─────────────────────────────────────────────
module "alb_portfolio" {
  source = "../../../modules/alb"

  project_name          = "mecandjeo-portfolio"
  environment           = var.environment
  vpc_id                = local.vpc_id
  public_subnet_ids     = local.public_subnet_ids
  alb_security_group_id = local.alb_security_group_id
  container_port        = var.portfolio_port
  health_check_path     = "/health"
}

# ── Portfolio ECS ─────────────────────────────────────────────
module "ecs_portfolio" {
  source = "../../../modules/ecs"

  project_name                = "mecandjeo-portfolio"
  environment                 = var.environment
  aws_region                  = var.aws_region
  vpc_id                      = local.vpc_id
  public_subnet_ids           = local.public_subnet_ids
  ecs_security_group_id       = local.ecs_security_group_id
  ecs_task_execution_role_arn = local.ecs_task_execution_role_arn
  container_image             = var.portfolio_image
  container_port              = var.portfolio_port
  task_cpu                    = var.task_cpu
  task_memory                 = var.task_memory
  desired_count               = var.desired_count
  target_group_arn            = module.alb_portfolio.target_group_arn
  app_environment             = var.environment
  app_project_name            = "mecandjeo-portfolio"
  app_version                 = "1.0.0"
}

# ── Portfolio Auto Scaling ────────────────────────────────────
module "autoscaling_portfolio" {
  source = "../../../modules/autoscaling"

  project_name            = "mecandjeo-portfolio"
  environment             = var.environment
  ecs_cluster_name        = module.ecs_portfolio.ecs_cluster_name
  ecs_service_name        = module.ecs_portfolio.ecs_service_name
  min_capacity            = var.min_capacity
  max_capacity            = var.max_capacity
  scale_out_cpu_threshold = var.scale_out_cpu_threshold
  scale_in_cpu_threshold  = var.scale_in_cpu_threshold
}

# ─────────────────────────────────────────────────────────────
# Outputs
# ─────────────────────────────────────────────────────────────
output "portfolio_alb_dns_name" {
  description = "Portfolio ALB DNS name — open in browser"
  value       = module.alb_portfolio.alb_dns_name
}

output "portfolio_ecs_cluster" {
  description = "Portfolio ECS cluster name"
  value       = module.ecs_portfolio.ecs_cluster_name
}

output "portfolio_cloudwatch_log_group" {
  description = "Portfolio CloudWatch log group"
  value       = module.ecs_portfolio.cloudwatch_log_group_name
}