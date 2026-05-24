# ─────────────────────────────────────────────────────────────
# Dashboard Application — Dev
# State key: mecandjeo-dashboard/dev/terraform.tfstate
#
# Deploys dashboard ALB, ECS, and autoscaling only.
# Shared infrastructure read from shared state.
# ─────────────────────────────────────────────────────────────

# ── Read Shared Infrastructure ────────────────────────────────
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

# ── Dashboard ALB ─────────────────────────────────────────────
module "alb" {
  source = "../../../modules/alb"

  project_name          = "mecandjeo-infra"
  environment           = var.environment
  vpc_id                = local.vpc_id
  public_subnet_ids     = local.public_subnet_ids
  alb_security_group_id = local.alb_security_group_id
  container_port        = var.container_port
  health_check_path     = var.health_check_path
}

# ── Dashboard ECS ─────────────────────────────────────────────
module "ecs" {
  source = "../../../modules/ecs"

  project_name                = "mecandjeo-infra"
  environment                 = var.environment
  aws_region                  = var.aws_region
  vpc_id                      = local.vpc_id
  public_subnet_ids           = local.public_subnet_ids
  ecs_security_group_id       = local.ecs_security_group_id
  ecs_task_execution_role_arn = local.ecs_task_execution_role_arn
  container_image             = var.container_image
  container_port              = var.container_port
  task_cpu                    = var.task_cpu
  task_memory                 = var.task_memory
  desired_count               = var.desired_count
  target_group_arn            = module.alb.target_group_arn
  app_environment             = var.environment
  app_project_name            = "mecandjeo-infra"
  app_version                 = "1.0.0"
}

# ── Dashboard Auto Scaling ────────────────────────────────────
module "autoscaling" {
  source = "../../../modules/autoscaling"

  project_name            = "mecandjeo-infra"
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

output "ecs_cluster_name" {
  description = "Dashboard ECS cluster name"
  value       = module.ecs.ecs_cluster_name
}

output "cloudwatch_log_group" {
  description = "Dashboard CloudWatch log group"
  value       = module.ecs.cloudwatch_log_group_name
}