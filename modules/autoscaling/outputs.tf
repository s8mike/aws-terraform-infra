output "scale_out_policy_arn" {
  description = "ARN of the scale out policy"
  value       = aws_appautoscaling_policy.scale_out.arn
}

output "scale_in_policy_arn" {
  description = "ARN of the scale in policy"
  value       = aws_appautoscaling_policy.scale_in.arn
}

output "scale_out_alarm_name" {
  description = "Name of the scale out CloudWatch alarm"
  value       = aws_cloudwatch_metric_alarm.scale_out.alarm_name
}

output "scale_in_alarm_name" {
  description = "Name of the scale in CloudWatch alarm"
  value       = aws_cloudwatch_metric_alarm.scale_in.alarm_name
}