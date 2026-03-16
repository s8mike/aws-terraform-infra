locals {
  all_traffic_cidr = "0.0.0.0/0"
}

# Security Group for EC2
resource "aws_security_group" "ec2" {
  name        = "${var.project_name}-${var.environment}-ec2-sg"
  description = "Security group for EC2 instance - allows SSH from trusted IP only"
  vpc_id      = var.vpc_id

  ingress {
    description = "SSH from trusted IP only"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.allowed_ssh_cidr]
  }

  egress {
    description = "Allow all outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = [local.all_traffic_cidr]
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-ec2-sg"
  }
}

# Key Pair
resource "aws_key_pair" "main" {
  key_name   = "${var.project_name}-${var.environment}-keypair"
  public_key = file("~/.ssh/id_ed25519.pub")

  tags = {
    Name = "${var.project_name}-${var.environment}-keypair"
  }
}

# EC2 Instance
resource "aws_instance" "main" {
  ami                         = var.ami_id
  instance_type               = var.instance_type
  subnet_id                   = var.public_subnet_id
  vpc_security_group_ids      = [aws_security_group.ec2.id]
  key_name                    = aws_key_pair.main.key_name
  associate_public_ip_address = true

  tags = {
    Name = "${var.project_name}-${var.environment}-ec2"
  }
}

# 🧠 Notice we introduced locals here — the all_traffic_cidr local is used in the egress rule. This is the pattern we discussed earlier, applied for the first time.