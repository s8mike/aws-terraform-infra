locals {
  all_traffic_cidr = "0.0.0.0/0"
}

# ─────────────────────────────────────────
# Application Load Balancer
# ─────────────────────────────────────────
resource "aws_lb" "main" {
  #checkov:skip=CKV_AWS_150:Deletion protection is configurable but disabled by default; enable per environment.
  #checkov:skip=CKV_AWS_91:Access logging is configurable but disabled by default; requires a compatible S3 bucket.
  #checkov:skip=CKV2_AWS_28:WAF association is configurable but disabled by default; requires a verified Web ACL.
  #checkov:skip=CKV2_AWS_20:HTTP-to-HTTPS redirect is configurable but disabled by default.
  name                       = "${var.project_name}-${var.environment}-alb"
  internal                   = false # Internet-facing ALB (set to true for internal ALB)
  load_balancer_type         = "application"
  security_groups            = [var.alb_security_group_id]
  subnets                    = var.public_subnet_ids
  drop_invalid_header_fields = true # added — CKV_AWS_131

  # Allow environments to enable protection against accidental ALB deletion.
  enable_deletion_protection = var.enable_deletion_protection
  # Send ALB access logs to an existing S3 bucket when enabled.
  dynamic "access_logs" {
    for_each = var.access_logs_enabled ? [1] : []

    content {
      enabled = true
      bucket  = var.access_logs_bucket
      prefix  = var.access_logs_prefix
    }
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-alb"
  }
}

# ─────────────────────────────────────────
# Target Group
# ─────────────────────────────────────────
resource "aws_lb_target_group" "main" {
  #checkov:skip=CKV_AWS_378:Target group uses HTTP; ALB-to-target encryption is not configured.
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
  #checkov:skip=CKV_AWS_2:HTTP listener retained for compatibility; HTTPS is optional and requires an ACM certificate.
  #checkov:skip=CKV_AWS_103:HTTP listener has no TLS; HTTPS listener is optional.
  load_balancer_arn = aws_lb.main.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type = var.http_to_https_redirect ? "redirect" : "forward"

    dynamic "redirect" {
      for_each = var.http_to_https_redirect ? [1] : []

      content {
        port        = "443"
        protocol    = "HTTPS"
        status_code = "HTTP_301"
      }
    }

    dynamic "forward" {
      for_each = var.http_to_https_redirect ? [] : [1]

      content {
        target_group {
          arn = aws_lb_target_group.main.arn
        }
      }
    }
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-http-listener"
  }
}

# Create an HTTPS listener only when HTTPS is enabled.
resource "aws_lb_listener" "https" {
  count = var.https_enabled ? 1 : 0

  load_balancer_arn = aws_lb.main.arn
  port              = 443
  protocol          = "HTTPS"
  certificate_arn   = var.acm_certificate_arn
  ssl_policy        = "ELBSecurityPolicy-TLS13-1-2-2021-06"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.main.arn
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-https-listener"
  }
}

# Associate an existing WAF Web ACL with the ALB when an ARN is provided.
resource "aws_wafv2_web_acl_association" "main" {
  count = var.waf_web_acl_arn != null ? 1 : 0

  resource_arn = aws_lb.main.arn
  web_acl_arn  = var.waf_web_acl_arn
}