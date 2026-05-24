# ─────────────────────────────────────────────────────────────
# School Application — Dev
# State key: mecandjeo-school/dev/terraform.tfstate
#
# Deploys school ALB, ECS, and autoscaling only.
# Shared infrastructure read from shared state.
# Port: 8002
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

# ── School ALB ────────────────────────────────────────────────
module "alb_school" {
  source = "../../../modules/alb"

  project_name          = "mecandjeo-school"
  environment           = var.environment
  vpc_id                = local.vpc_id
  public_subnet_ids     = local.public_subnet_ids
  alb_security_group_id = local.alb_security_group_id
  container_port        = var.container_port
  health_check_path     = var.health_check_path
}

# ── School ECS ────────────────────────────────────────────────
module "ecs_school" {
  source = "../../../modules/ecs"

  project_name                = "mecandjeo-school"
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
  target_group_arn            = module.alb_school.target_group_arn
  app_environment             = var.environment
  app_project_name            = "mecandjeo-school"
  app_version                 = "1.0.0"
}

# ── School Auto Scaling ───────────────────────────────────────
module "autoscaling_school" {
  source = "../../../modules/autoscaling"

  project_name            = "mecandjeo-school"
  environment             = var.environment
  ecs_cluster_name        = module.ecs_school.ecs_cluster_name
  ecs_service_name        = module.ecs_school.ecs_service_name
  min_capacity            = var.min_capacity
  max_capacity            = var.max_capacity
  scale_out_cpu_threshold = var.scale_out_cpu_threshold
  scale_in_cpu_threshold  = var.scale_in_cpu_threshold
}

# ─────────────────────────────────────────────────────────────
# Outputs
# ─────────────────────────────────────────────────────────────
output "school_alb_dns_name" {
  description = "School ALB DNS name"
  value       = module.alb_school.alb_dns_name
}

output "school_ecs_cluster" {
  description = "School ECS cluster name"
  value       = module.ecs_school.ecs_cluster_name
}

output "school_cloudwatch_log_group" {
  description = "School CloudWatch log group"
  value       = module.ecs_school.cloudwatch_log_group_name
}