# ─────────────────────────────────────────
# ECR Repository
# ─────────────────────────────────────────
resource "aws_ecr_repository" "main" {
  name                 = "${var.project_name}-${var.environment}"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-ecr"
  }
}

# ─────────────────────────────────────────
# CloudWatch Log Group
# ─────────────────────────────────────────
resource "aws_cloudwatch_log_group" "ecs" {
  name              = "/ecs/${var.project_name}-${var.environment}"
  retention_in_days = 7

  tags = {
    Name = "${var.project_name}-${var.environment}-ecs-logs"
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

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.ecs.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "ecs"
        }
      }

      healthCheck = {
        command     = ["CMD-SHELL", "curl -f http://localhost/ || exit 1"]
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
  name            = "${var.project_name}-${var.environment}-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.main.arn
  desired_count   = var.desired_count
  launch_type     = "FARGATE"

  # network_configuration {            # commented out temporarily for testing with public subnets
  #   subnets          = var.private_subnet_ids
  #   security_groups  = [var.ecs_security_group_id]
  #   assign_public_ip = false
  # }

  network_configuration {                          # added temporarily for testing with public subnets
  subnets          = var.public_subnet_ids
  security_groups  = [var.ecs_security_group_id]
  assign_public_ip = true
}

  # Load balancer attachment will be added in Stage 6
  # lifecycle {
  #   ignore_changes = [task_definition]
  # }

  tags = {
    Name = "${var.project_name}-${var.environment}-service"
  }

  depends_on = [aws_ecs_task_definition.main]
}


