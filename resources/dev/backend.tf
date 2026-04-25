terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

#   # # We will activate this in Stage 7 when we set up S3 remote state
#   backend "s3" {
#     bucket         = "mecandjeo-infra-dev-tfstate"
#     key            = "dev/terraform.tfstate"
#     region         = "us-east-1"
#     dynamodb_table = "mecandjeo-infra-dev-tfstate-lock"
#     encrypt        = true
#   }
# }

# provider "aws" {
#   region = var.aws_region

#   default_tags {
#     tags = {
#       Environment = "dev"
#       Project     = "mecandjeo-infra"
#       ManagedBy   = "Terraform"
#     }
#   }
}