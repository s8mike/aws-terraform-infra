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
  public_key = file("~/.ssh/id_ed25519.pub")

  tags = {
    Name = "${var.project_name}-${var.environment}-keypair"
  }
}

# ─────────────────────────────────────────
# EC2 Instance
# ─────────────────────────────────────────
resource "aws_instance" "main" {
  ami                         = data.aws_ami.amazon_linux_2023.id  # Now we are using the data source to fetch the latest Amazon Linux 2023 AMI dynamically
  instance_type               = var.instance_type
  subnet_id                   = var.public_subnet_id
  vpc_security_group_ids      = [var.security_group_id]
  key_name                    = aws_key_pair.main.key_name
  associate_public_ip_address = true

  tags = {
    Name = "${var.project_name}-${var.environment}-ec2"
  }
}



##############################################################################################
## FIRST CODE AT STAGE 3
# # Key Pair
# resource "aws_key_pair" "main" {
#   key_name   = "${var.project_name}-${var.environment}-keypair"
#   public_key = file("~/.ssh/id_ed25519.pub")

#   tags = {
#     Name = "${var.project_name}-${var.environment}-keypair"
#   }
# }

# # EC2 Instance
# resource "aws_instance" "main" {
#   ami                         = var.ami_id           # this was obtained from the console, but you can also use the aws_ami data source to fetch it dynamically at next stage
#   instance_type               = var.instance_type
#   subnet_id                   = var.public_subnet_id
#   vpc_security_group_ids      = [var.security_group_id]
#   key_name                    = aws_key_pair.main.key_name
#   associate_public_ip_address = true

#   tags = {
#     Name = "${var.project_name}-${var.environment}-ec2"
#   }
# }