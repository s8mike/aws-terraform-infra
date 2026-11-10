# Phase 9: RDS connection details used to construct the application secret.
output "endpoint" {
  value = aws_db_instance.database.address
}

output "port" {
  value = aws_db_instance.database.port
}

output "database_name" {
  value = aws_db_instance.database.db_name
}

output "master_user_secret_arn" {
  value     = aws_db_instance.database.master_user_secret[0].secret_arn
  sensitive = true
}
