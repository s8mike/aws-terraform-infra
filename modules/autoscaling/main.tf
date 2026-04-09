# ─────────────────────────────────────────
# App Auto Scaling Target
# ─────────────────────────────────────────
resource "aws_appautoscaling_target" "ecs" {
  max_capacity       = var.max_capacity
  min_capacity       = var.min_capacity
  resource_id        = "service/${var.ecs_cluster_name}/${var.ecs_service_name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}

# ─────────────────────────────────────────
# Scale Out Policy — Add Tasks
# ─────────────────────────────────────────
resource "aws_appautoscaling_policy" "scale_out" {
  name               = "${var.project_name}-${var.environment}-scale-out"
  policy_type        = "StepScaling"
  resource_id        = aws_appautoscaling_target.ecs.resource_id
  scalable_dimension = aws_appautoscaling_target.ecs.scalable_dimension
  service_namespace  = aws_appautoscaling_target.ecs.service_namespace

  step_scaling_policy_configuration {
    adjustment_type         = "ChangeInCapacity"
    cooldown                = 60     # seconds-respond fast to traffic spikes
    metric_aggregation_type = "Average"

    step_adjustment {
      metric_interval_lower_bound = 0
      scaling_adjustment          = 1
    }
  }
}

# ─────────────────────────────────────────
# Scale In Policy — Remove Tasks
# ─────────────────────────────────────────
resource "aws_appautoscaling_policy" "scale_in" {
  name               = "${var.project_name}-${var.environment}-scale-in"
  policy_type        = "StepScaling"
  resource_id        = aws_appautoscaling_target.ecs.resource_id
  scalable_dimension = aws_appautoscaling_target.ecs.scalable_dimension
  service_namespace  = aws_appautoscaling_target.ecs.service_namespace

  step_scaling_policy_configuration {
    adjustment_type         = "ChangeInCapacity"
    cooldown                = 300      
    metric_aggregation_type = "Average"

    step_adjustment {
      metric_interval_upper_bound = 0
      scaling_adjustment          = -1
    }
  }
}

# ─────────────────────────────────────────
# CloudWatch Alarm — Trigger Scale Out
# ─────────────────────────────────────────
resource "aws_cloudwatch_metric_alarm" "scale_out" {
  alarm_name          = "${var.project_name}-${var.environment}-cpu-scale-out"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2   # must exceed threshold for 2 minutes before scaling out  
  metric_name         = "CPUUtilization"
  namespace           = "AWS/ECS"
  period              = 60   
  statistic           = "Average"
  threshold           = var.scale_out_cpu_threshold
  alarm_description   = "Scale out when CPU exceeds ${var.scale_out_cpu_threshold}%"
  alarm_actions       = [aws_appautoscaling_policy.scale_out.arn]

  dimensions = {
    ClusterName = var.ecs_cluster_name
    ServiceName = var.ecs_service_name
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-cpu-scale-out"
  }
}

# ─────────────────────────────────────────
# CloudWatch Alarm — Trigger Scale In
# ─────────────────────────────────────────
resource "aws_cloudwatch_metric_alarm" "scale_in" {
  alarm_name          = "${var.project_name}-${var.environment}-cpu-scale-in"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = 5
  metric_name         = "CPUUtilization"
  namespace           = "AWS/ECS"
  period              = 60
  statistic           = "Average"
  threshold           = var.scale_in_cpu_threshold
  alarm_description   = "Scale in when CPU drops below ${var.scale_in_cpu_threshold}%"
  alarm_actions       = [aws_appautoscaling_policy.scale_in.arn]

  dimensions = {
    ClusterName = var.ecs_cluster_name
    ServiceName = var.ecs_service_name
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-cpu-scale-in"
  }
}