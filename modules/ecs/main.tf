## ─────────────────────────────────────────
# ECR Repository
## ─────────────────────────────────────────
## Removed from Terraform management — ECR repository created manually
## and preserved permanently outside terraform destroy. This will be uncommented later.
# resource "aws_ecr_repository" "main" {
#   name                 = "${var.project_name}-${var.environment}"
#   image_tag_mutability = "MUTABLE"
#
#   image_scanning_configuration {
#     scan_on_push = true
#   }
#
#   tags = {
#     Name = "${var.project_name}-${var.environment}-ecr"
#   }
# }

# ─────────────────────────────────────────
# CloudWatch Log Group
# ─────────────────────────────────────────
resource "aws_cloudwatch_log_group" "ecs" {
  # Retain ECS logs for the configured period and optionally encrypt
  # them with a customer-managed KMS key when one is provided.
  name              = "/ecs/${var.project_name}-${var.environment}"
  retention_in_days = var.log_retention_in_days
  kms_key_id        = var.log_kms_key_id

  tags = {
    Name        = "${var.project_name}-${var.environment}-logs"
    Environment = var.environment
  }
}

# ─────────────────────────────────────────
# ECS Cluster
# ─────────────────────────────────────────
resource "aws_ecs_cluster" "main" {
  name = "${var.project_name}-${var.environment}-cluster"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-cluster"
  }
}

# ─────────────────────────────────────────
# ECS Task Definition
# ─────────────────────────────────────────
resource "aws_ecs_task_definition" "main" {
  family                   = "${var.project_name}-${var.environment}-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.task_cpu
  memory                   = var.task_memory
  execution_role_arn       = var.ecs_task_execution_role_arn

  container_definitions = jsonencode([
    {
      name      = "${var.project_name}-${var.environment}-container"
      image     = var.container_image
      essential = true

      portMappings = [
        {
          containerPort = var.container_port
          hostPort      = var.container_port
          protocol      = "tcp"
        }
      ]

      # Environment variables passed to the FastAPI application
      environment = [
        {
          name  = "ENVIRONMENT"
          value = var.app_environment
        },
        {
          name  = "PROJECT_NAME"
          value = var.app_project_name
        },
        {
          name  = "AWS_REGION"
          value = var.aws_region
        },
        {
          name  = "APP_VERSION"
          value = var.app_version
        }
      ]

      # Inject DATABASE_URL and SECRET_KEY from AWS Secrets Manager
      # when both secret ARNs are provided; otherwise, pass no secrets.
      secrets = (
        var.database_url_secret_arn != null &&
        var.secret_key_secret_arn != null
        ) ? [
        {
          name      = "DATABASE_URL"
          valueFrom = var.database_url_secret_arn
        },
        {
          name      = "SECRET_KEY"
          valueFrom = var.secret_key_secret_arn
        }
      ] : []

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.ecs.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "ecs"
        }
      }

      healthCheck = {
        command = [
          "CMD-SHELL",
          "python -c \"import urllib.request; urllib.request.urlopen('http://localhost:${var.container_port}/health')\""
        ]
        interval    = 30
        timeout     = 5
        retries     = 3
        startPeriod = 60
      }
    }
  ])

  tags = {
    Name = "${var.project_name}-${var.environment}-task"
  }
}

# ─────────────────────────────────────────
# ECS Service
# ─────────────────────────────────────────
resource "aws_ecs_service" "main" {
  #checkov:skip=CKV_AWS_333:Public IP assignment is configurable; enabled for current environments without private-subnet egress.
  name            = "${var.project_name}-${var.environment}-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.main.arn
  desired_count   = var.desired_count
  launch_type     = "FARGATE"

  # Ensure at least one task is always healthy during deployment
  deployment_minimum_healthy_percent = 100
  deployment_maximum_percent         = 200

  # ➕ ADDED: prevents premature health check failures during startup
  health_check_grace_period_seconds = 60

  # ➕ ADDED: automatic rollback if deployment fails
  deployment_circuit_breaker {
    enable   = true
    rollback = true
  }

  # network_configuration {            # commented out temporarily for testing with public subnets. In production, we will use private subnets and NAT gateways for better security.
  #   subnets          = var.private_subnet_ids
  #   security_groups  = [var.ecs_security_group_id]
  #   assign_public_ip = false
  # }

  network_configuration {
    subnets          = var.subnet_ids
    security_groups  = [var.ecs_security_group_id]
    assign_public_ip = var.assign_public_ip
  }

  # ALB Block added at stage 6 to register ECS tasks with the ALB target group created in the load balancer module. This allows the ALB to route traffic to the ECS tasks.
  load_balancer {
    target_group_arn = var.target_group_arn
    container_name   = "${var.project_name}-${var.environment}-container"
    container_port   = var.container_port
  }


  tags = {
    Name = "${var.project_name}-${var.environment}-service"
  }

  depends_on = [aws_ecs_task_definition.main]
}

#   # lifecycle {
#   #   ignore_changes = [task_definition]
#   # }
# }