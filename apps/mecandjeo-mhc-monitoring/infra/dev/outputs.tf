# Phase 9: deployment outputs used by CI/CD and post-deployment verification.
output "mhc_alb_dns_name" {
  value = module.alb.alb_dns_name
}

output "mhc_ecs_cluster_name" {
  value = module.ecs.ecs_cluster_name
}

output "mhc_ecs_service_name" {
  value = module.ecs.ecs_service_name
}

output "mhc_cloudwatch_log_group" {
  value = module.ecs.cloudwatch_log_group_name
}

output "rds_endpoint" {
  value = module.database.endpoint
}

output "rds_master_user_secret_arn" {
  value     = module.database.master_user_secret_arn
  sensitive = true
}
