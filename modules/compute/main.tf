# ─────────────────────────────────────────
# Data Source — Latest Amazon Linux 2023 AMI
# ─────────────────────────────────────────
data "aws_ami" "amazon_linux_2023" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-*-x86_64"]
  }

  filter {
    name   = "state"
    values = ["available"]
  }
}

# ─────────────────────────────────────────
# Key Pair
# ─────────────────────────────────────────
resource "aws_key_pair" "main" {
  key_name   = "${var.project_name}-${var.environment}-keypair"
  public_key = var.public_key

  tags = {
    Name = "${var.project_name}-${var.environment}-keypair"
  }
}

# ─────────────────────────────────────────
# EC2 Instance
# ─────────────────────────────────────────
resource "aws_instance" "main" {
  # checkov:skip=CKV_AWS_88:Public IP retained for SSH bastion access; inbound SSH is restricted to the configured trusted CIDR.
  # checkov:skip=CKV2_AWS_41:No IAM role attached because the bastion has no current AWS API access requirement.
  ami                         = data.aws_ami.amazon_linux_2023.id
  instance_type               = var.instance_type
  subnet_id                   = var.public_subnet_id
  vpc_security_group_ids      = [var.security_group_id]
  key_name                    = aws_key_pair.main.key_name
  associate_public_ip_address = true

  # Keep your existing metadata_options, ebs_optimized, root_block_device,
  # and tags unchanged.

  # Require IMDSv2 to reduce metadata-service exposure.
  metadata_options {
    http_endpoint               = "enabled"
    http_tokens                 = "required"
    http_put_response_hop_limit = 1
  }

  # Publish EC2 metrics to CloudWatch at 1-minute intervals.
  monitoring = true

  # Enable EBS optimization where supported by the instance type.
  ebs_optimized = true

  # Encrypt the root EBS volume.
  root_block_device {
    encrypted = true
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-instance"
  }
}
