# Phase 9: private PostgreSQL database for the MHC monitoring application.
resource "aws_security_group" "database" {
  name        = "${var.project_name}-${var.environment}-rds-sg"
  description = "Allow PostgreSQL traffic only from MHC ECS tasks"
  vpc_id      = var.vpc_id

  ingress {
    description     = "PostgreSQL from MHC ECS tasks"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [var.ecs_security_group_id]
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-rds-sg"
  }
}

resource "aws_db_subnet_group" "database" {
  name       = "${var.project_name}-${var.environment}-rds-subnets"
  subnet_ids = var.private_subnet_ids

  tags = {
    Name = "${var.project_name}-${var.environment}-rds-subnets"
  }
}

resource "aws_db_instance" "database" {
  identifier                   = "${var.project_name}-${var.environment}-postgres"
  engine                       = "postgres"
  engine_version               = var.engine_version
  instance_class               = var.instance_class
  allocated_storage            = var.allocated_storage
  max_allocated_storage        = var.max_allocated_storage
  storage_type                 = "gp3"
  storage_encrypted            = true
  db_name                      = var.database_name
  username                     = var.database_username
  manage_master_user_password  = true
  db_subnet_group_name         = aws_db_subnet_group.database.name
  vpc_security_group_ids       = [aws_security_group.database.id]
  publicly_accessible          = false
  multi_az                     = false
  backup_retention_period      = var.backup_retention_period
  copy_tags_to_snapshot        = true
  deletion_protection          = var.deletion_protection
  skip_final_snapshot          = var.skip_final_snapshot
  auto_minor_version_upgrade   = true
  performance_insights_enabled = false

  tags = {
    Name = "${var.project_name}-${var.environment}-postgres"
  }
}
