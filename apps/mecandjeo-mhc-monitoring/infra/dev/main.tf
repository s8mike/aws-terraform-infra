# Phase 9: MHC app resources consume shared network infrastructure through remote state.
data "terraform_remote_state" "shared" {
  backend = "s3"

  config = {
    bucket = "mecandjeo-infra-dev-tfstate"
    key    = "mecandjeo-shared/dev/terraform.tfstate"
    region = var.aws_region
  }
}

locals {
  vpc_id                = data.terraform_remote_state.shared.outputs.vpc_id
  public_subnet_ids     = data.terraform_remote_state.shared.outputs.public_subnet_ids
  private_subnet_ids    = data.terraform_remote_state.shared.outputs.private_subnet_ids
  alb_security_group_id = data.terraform_remote_state.shared.outputs.alb_security_group_id
  ecs_security_group_id = data.terraform_remote_state.shared.outputs.ecs_security_group_id
  application_secret_arns = compact([
    var.database_url_secret_arn,
    var.secret_key_secret_arn,
  ])
}

# Dedicated execution role prevents this app from inheriting other apps' secret access.
resource "aws_iam_role" "ecs_task_execution" {
  name = "${var.project_name}-${var.environment}-ecs-execution"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = { Service = "ecs-tasks.amazonaws.com" }
      Action = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_task_execution" {
  role       = aws_iam_role.ecs_task_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role_policy" "read_application_secrets" {
  count = length(local.application_secret_arns) > 0 ? 1 : 0

  name = "${var.project_name}-${var.environment}-read-secrets"
  role = aws_iam_role.ecs_task_execution.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["secretsmanager:GetSecretValue"]
      Resource = local.application_secret_arns
    }]
  })
}

# The task role is intentionally empty until the application needs AWS runtime APIs.
resource "aws_iam_role" "ecs_task" {
  name = "${var.project_name}-${var.environment}-ecs-task"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = { Service = "ecs-tasks.amazonaws.com" }
      Action = "sts:AssumeRole"
    }]
  })
}

module "database" {
  source = "../modules/rds-postgres"

  project_name          = var.project_name
  environment           = var.environment
  vpc_id                = local.vpc_id
  private_subnet_ids    = local.private_subnet_ids
  ecs_security_group_id = local.ecs_security_group_id
  instance_class        = var.rds_instance_class
  deletion_protection   = var.rds_deletion_protection
}

module "alb" {
  source = "../../../../modules/alb"

  project_name          = var.project_name
  environment           = var.environment
  vpc_id                = local.vpc_id
  public_subnet_ids     = local.public_subnet_ids
  alb_security_group_id = local.alb_security_group_id
  container_port        = var.container_port
  health_check_path     = "/health"
}

module "ecs" {
  source = "../../../../modules/ecs"

  project_name                = var.project_name
  environment                 = var.environment
  aws_region                  = var.aws_region
  vpc_id                      = local.vpc_id
  subnet_ids                  = local.public_subnet_ids
  assign_public_ip            = true
  ecs_security_group_id       = local.ecs_security_group_id
  ecs_task_execution_role_arn = aws_iam_role.ecs_task_execution.arn
  ecs_task_role_arn           = aws_iam_role.ecs_task.arn
  container_image             = var.container_image
  container_port              = var.container_port
  task_cpu                    = var.task_cpu
  task_memory                 = var.task_memory
  desired_count               = var.desired_count
  target_group_arn            = module.alb.target_group_arn
  app_environment             = var.environment
  app_project_name            = var.project_name
  app_version                 = "0.7.0"
  database_url_secret_arn     = var.database_url_secret_arn
  secret_key_secret_arn       = var.secret_key_secret_arn
}

module "autoscaling" {
  source = "../../../../modules/autoscaling"

  project_name            = var.project_name
  environment             = var.environment
  ecs_cluster_name        = module.ecs.ecs_cluster_name
  ecs_service_name        = module.ecs.ecs_service_name
  min_capacity            = var.min_capacity
  max_capacity            = var.max_capacity
  scale_out_cpu_threshold = 70
  scale_in_cpu_threshold  = 30
}
