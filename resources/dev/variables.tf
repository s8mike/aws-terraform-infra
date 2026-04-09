# resources/dev/variables.tf

variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
}

variable "project_name" {
  description = "Project name prefix for all resources"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
}

variable "public_subnet_cidrs" {
  description = "List of CIDR blocks for public subnets"
  type        = list(string)
}

variable "private_subnet_cidrs" {
  description = "List of CIDR blocks for private subnets"
  type        = list(string)
}

variable "availability_zones" {
  description = "List of availability zones"
  type        = list(string)
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.micro"
}

# variable "ami_id" {                          # Uncomment if you want to specify a custom AMI ID (Stage 3). Otherwise, you can use a data source to fetch the latest Amazon Linux 2 AMI.
#   description = "AMI ID for the EC2 instance"
#   type        = string
# }

variable "allowed_ssh_cidr" {
  description = "Trusted IP CIDR allowed to SSH into the EC2 instance"
  type        = string
}

# Additional variables for Fargate and ECS

# ECS Variables — Stage 5
variable "container_image" {
  description = "Docker image to run in ECS"
  type        = string
  default     = "nginx:latest"
}

variable "container_port" {
  description = "Port the container listens on"
  type        = number
  default     = 80
}

variable "task_cpu" {
  description = "CPU units for the ECS task"
  type        = number
  default     = 256
}

variable "task_memory" {
  description = "Memory in MB for the ECS task"
  type        = number
  default     = 512
}

variable "desired_count" {
  description = "Desired number of ECS tasks"
  type        = number
  default     = 2
}

variable "health_check_path" {
  description = "Path for ALB health checks"
  type        = string
  default     = "/"
}