locals {
  all_traffic_cidr = "0.0.0.0/0"
}

# ─────────────────────────────────────────
# Application Load Balancer
# ─────────────────────────────────────────
resource "aws_lb" "main" {
  #checkov:skip=CKV_AWS_150:Deletion protection disabled intentionally in dev
  #checkov:skip=CKV_AWS_91:Access logging requires S3 bucket — deferred to prod
  #checkov:skip=CKV2_AWS_28:WAF protection deferred to production
  #checkov:skip=CKV2_AWS_20:HTTPS redirect requires certificate — prod only
  name                       = "${var.project_name}-${var.environment}-alb"
  internal                   = false # Internet-facing ALB (set to true for internal ALB)
  load_balancer_type         = "application"
  security_groups            = [var.alb_security_group_id]
  subnets                    = var.public_subnet_ids
  drop_invalid_header_fields = true # added — CKV_AWS_131

  # Set to true (production) if you want to prevent accidental deletion
  enable_deletion_protection = false # Allows terraform destory. 

  tags = {
    Name = "${var.project_name}-${var.environment}-alb"
  }
}

# ─────────────────────────────────────────
# Target Group
# ─────────────────────────────────────────
resource "aws_lb_target_group" "main" {
  #checkov:skip=CKV_AWS_378:HTTP protocol used in dev — HTTPS in prod
  name        = "${var.project_name}-${var.environment}-tg"
  port        = var.container_port
  protocol    = "HTTP"
  vpc_id      = var.vpc_id
  target_type = "ip" #Required for ECS (Fargate)- tasks are registered by IP address not instance ID

  health_check {
    enabled             = true
    healthy_threshold   = 2
    unhealthy_threshold = 3
    timeout             = 5
    interval            = 30
    path                = var.health_check_path
    matcher             = "200"
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-tg"
  }
}

# ─────────────────────────────────────────
# HTTP Listener
# ─────────────────────────────────────────
resource "aws_lb_listener" "http" {
  #checkov:skip=CKV_AWS_2:HTTPS requires ACM certificate — prod only
  #checkov:skip=CKV_AWS_103:TLS requires HTTPS listener — prod only
  load_balancer_arn = aws_lb.main.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.main.arn
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-http-listener"
  }
}