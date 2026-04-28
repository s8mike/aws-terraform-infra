
---

## Phase 3 — Deploy to AWS via Terraform

---

### What We Are Doing in This Phase

We are updating the Terraform configuration to point to our real application image instead of nginx, then running `terraform apply` to deploy the MecanjeoOps Dashboard to AWS. By the end of this phase the dashboard will be live and accessible from any browser via the ALB DNS name.

```
Phase 2 — Image in ECR and Docker Hub
        │
        ▼
Phase 3 (This Phase)
  ├── Update terraform.tfvars → container_image points to ECR
  ├── Update terraform.tfvars → container_port changed to 8000
  ├── Update terraform.tfvars → health_check_path changed to /health
  ├── Update modules/ecs → pass environment variables to container
  ├── terraform init → connect to S3 backend
  ├── terraform plan → review 37 resources
  └── terraform apply → deploy to AWS
        │
        ▼
Live application at ALB DNS name
```

---

### What Changes From the nginx Deployment

Three things change in our Terraform configuration. Everything else — VPC, security groups, IAM, ALB, auto scaling, remote state — stays exactly the same.

| Setting               | Before (nginx) | After (Dashboard)                                          |
|-----------------------|----------------|------------------------------------------------------------|
| `container_image`     | `nginx:latest` | ECR image URI                                              |
| `container_port`      | `80`           | `8000`                                                     |
| `health_check_path`   | `/`            | `/health`                                                  |
| Environment variables | None           | `ENVIRONMENT`, `PROJECT_NAME`, `AWS_REGION`, `APP_VERSION` |

---

### Step 1: Update `terraform.tfvars`

Open `resources/dev/terraform.tfvars` and replace the entire file with:

```hcl
# General
aws_region   = "us-east-1"
project_name = "mecandjeo-infra"
environment  = "dev"

# VPC
vpc_cidr             = "10.0.0.0/16"
public_subnet_cidrs  = ["10.0.1.0/24", "10.0.2.0/24"]
private_subnet_cidrs = ["10.0.3.0/24", "10.0.4.0/24"]
availability_zones   = ["us-east-1a", "us-east-1b"]

# Compute
instance_type    = "t3.micro"
allowed_ssh_cidr = "YOUR_IP/32"

# ECS — Updated for MecanjeoOps Dashboard
container_image   = "776735193826.dkr.ecr.us-east-1.amazonaws.com/mecandjeo-infra-dev:v1.0.0"
container_port    = 8000
task_cpu          = 256
task_memory       = 512
desired_count     = 2
health_check_path = "/health"

# Auto Scaling
min_capacity            = 2
max_capacity            = 6
scale_out_cpu_threshold = 70
scale_in_cpu_threshold  = 30
```

> ⚠️ Replace `YOUR_IP/32` with your current IP from `curl ifconfig.me`

---

### Step 2: Update the Variables File

Open `resources/dev/variables.tf` and confirm `container_port` and `health_check_path` have the correct types. The file should already have these — just verify:

```hcl
variable "container_port" {
  description = "Port the container listens on"
  type        = number
  default     = 8000
}

variable "health_check_path" {
  description = "Path for ALB health checks"
  type        = string
  default     = "/health"
}
```

---

### Step 3: Update the ECS Module to Pass Environment Variables

This is the most important change. Our FastAPI application reads `ENVIRONMENT`, `PROJECT_NAME`, `AWS_REGION`, and `APP_VERSION` from environment variables at runtime. We need to pass these into the ECS container definition.

Open `modules/ecs/variables.tf` and add these new variables at the bottom:

```hcl
variable "app_environment" {
  description = "Application environment name passed to container"
  type        = string
  default     = "dev"
}

variable "app_project_name" {
  description = "Project name passed to container"
  type        = string
  default     = "mecandjeo-infra"
}

variable "app_version" {
  description = "Application version passed to container"
  type        = string
  default     = "1.0.0"
}
```

Now open `modules/ecs/main.tf` and update the `container_definitions` block inside the task definition to include the environment variables. Find the `container_definitions` section and replace it with:

```hcl
container_definitions = jsonencode([
  {
    name      = "${var.project_name}-${var.environment}-container"
    image     = var.container_image
    essential = true

    portMappings = [
      {
        containerPort = var.container_port
        hostPort      = var.container_port
        protocol      = "tcp"
      }
    ]

    # Environment variables passed to the FastAPI application
    environment = [
      {
        name  = "ENVIRONMENT"
        value = var.app_environment
      },
      {
        name  = "PROJECT_NAME"
        value = var.app_project_name
      },
      {
        name  = "AWS_REGION"
        value = var.aws_region
      },
      {
        name  = "APP_VERSION"
        value = var.app_version
      }
    ]

    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = aws_cloudwatch_log_group.ecs.name
        "awslogs-region"        = var.aws_region
        "awslogs-stream-prefix" = "ecs"
      }
    }

    healthCheck = {
      command     = ["CMD-SHELL", "curl -f http://localhost:${var.container_port}/health || exit 1"]
      interval    = 30
      timeout     = 5
      retries     = 3
      startPeriod = 60
    }
  }
])
```

> 🧠 Two important changes here:
> - The `environment` block passes runtime config to the container — no hardcoded values
> - The `healthCheck` command now uses `/health` instead of `/` — matching our FastAPI health endpoint

---

### Step 4: Update the Dev Environment to Pass New Variables

Open `resources/dev/main.tf` and update the ECS module call to pass the new variables:

```hcl
module "ecs" {
  source = "../../modules/ecs"

  project_name                = var.project_name
  environment                 = var.environment
  aws_region                  = var.aws_region
  vpc_id                      = module.vpc.vpc_id
  public_subnet_ids           = module.vpc.public_subnet_ids
  ecs_security_group_id       = module.security.ecs_security_group_id
  ecs_task_execution_role_arn = module.security.ecs_task_execution_role_arn
  container_image             = var.container_image
  container_port              = var.container_port
  task_cpu                    = var.task_cpu
  task_memory                 = var.task_memory
  desired_count               = var.desired_count
  target_group_arn            = module.alb.target_group_arn

  # New — runtime environment variables for the application
  app_environment  = var.environment
  app_project_name = var.project_name
  app_version      = "1.0.0"
}
```

Also add these new variables to `resources/dev/variables.tf`:

```hcl
variable "app_version" {
  description = "Application version"
  type        = string
  default     = "1.0.0"
}
```

---

### Step 5: Update the ALB Security Group for Port 8000

Our application runs on port 8000, not port 80. We need to update the security groups to allow traffic on the correct port.

Open `modules/security/main.tf` and update the ECS security group ingress rule:

```hcl
# ECS Security Group
resource "aws_security_group" "ecs" {
  name        = "${var.project_name}-${var.environment}-ecs-sg"
  description = "Security group for ECS tasks - traffic from ALB only"
  vpc_id      = var.vpc_id

  ingress {
    description     = "Allow traffic from ALB only"
    from_port       = var.container_port
    to_port         = var.container_port
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }

  egress {
    description = "Allow all outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = [local.all_traffic_cidr]
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-ecs-sg"
  }
}
```

Now add `container_port` as a variable to `modules/security/variables.tf`:

```hcl
variable "container_port" {
  description = "Port the container listens on"
  type        = number
  default     = 8000
}
```

And pass it in `resources/dev/main.tf` security module call:

```hcl
module "security" {
  source = "../../modules/security"

  project_name     = var.project_name
  environment      = var.environment
  vpc_id           = module.vpc.vpc_id
  allowed_ssh_cidr = var.allowed_ssh_cidr
  container_port   = var.container_port
}
```

---

### Step 6: Run It

```bash
cd resources/dev

# Step 6a — Initialise Terraform and connect to S3 backend
terraform init

# Step 6b — Format all code
terraform fmt -recursive

# Step 6c — Validate configuration
terraform validate

# Step 6d — Preview what will be created
terraform plan
```

Expected resources — **37 to add:**

| Module       | Resources                                                                 | Count |
|--------------|---------------------------------------------------------------------------|-------|
| VPC          | VPC, IGW, 4 subnets, 2 route tables, 4 RT associations                    | 12    |
| Security     | EC2 SG, ALB SG, ECS SG, IAM role, policy attachment                       | 5     |
| Compute      | Key pair, EC2 instance                                                    | 2     |
| ALB          | ALB, target group, HTTP listener                                          | 3     |
| ECS          | ECR repo, CloudWatch log group, ECS cluster, task definition, ECS service | 5     |
| Remote State | S3 bucket, versioning, encryption, public access block, DynamoDB          | 5     |
| Auto Scaling | scaling target, 2 policies, 2 CloudWatch alarms                           | 5     |
| **Total**    |                                                                           | **37**|

Paste your `terraform plan` output count and we review before applying. 🚀