# Claude 2/5/26
---

# AWS Terraform Infrastructure Project
## Auto-Scaling Web Application Infrastructure on AWS with Terraform and GitHub Actions CI/CD

**Engineer:** Platform Engineering Intern — Mecandjeo Technology
**Repository:** github.com/s8mike/aws-terraform-infra
**Completed:** May 2026
**Infrastructure Stages:** 7
**Application Phases:** 4
**Total AWS Resources:** 31 (dev) | 31 (prod — ready)
**Cloud Provider:** AWS (us-east-1)
**IaC Tool:** Terraform >= 1.10.0
**CI/CD:** GitHub Actions

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Repository Structure](#2-repository-structure)
3. [Prerequisites](#3-prerequisites)
4. [Architecture](#4-architecture)
5. [Infrastructure — Stages 1-7](#5-infrastructure-stages-1-7)
6. [Application — Phases 1-4](#6-application-phases-1-4)
7. [Complete Resource Inventory](#7-complete-resource-inventory)
8. [Environment Configuration](#8-environment-configuration)
9. [Session Workflow](#9-session-workflow)
10. [CI/CD Pipeline](#10-cicd-pipeline)
11. [Production Readiness](#11-production-readiness)
12. [Operational Runbook](#12-operational-runbook)
13. [Key Lessons Learned](#13-key-lessons-learned)
14. [What You Can Say in Interviews](#14-what-you-can-say-in-interviews)

---

## 1. Project Overview

This project provisions a complete, production-grade, auto-scaling web application infrastructure on AWS entirely through Terraform, and deploys a real Python FastAPI application through a fully automated GitHub Actions CI/CD pipeline. Every resource — from networking to containers to load balancing to auto scaling — is defined as Infrastructure as Code, version controlled in Git, and deployable across multiple environments without a single manual console click.

### What This Project Demonstrates

- Designing and provisioning multi-tier VPC networking from scratch using Terraform
- Managing infrastructure across multiple environments with a monorepo pattern
- Deploying a real containerised Python application on ECS Fargate
- Implementing layered security with least-privilege IAM and security group chaining
- Exposing the application through an Application Load Balancer
- Automatically scaling containers based on CPU utilisation
- Managing Terraform state safely with S3 backend and native locking
- Writing reusable, composable Terraform modules with clean input/output interfaces
- Automating the full build-push-deploy cycle with GitHub Actions
- Pushing Docker images to both Docker Hub and AWS ECR simultaneously
- Separating sensitive secrets from non-sensitive configuration in CI/CD

---

## 2. Repository Structure

```
aws-terraform-infra/
│
├── modules/                         ← Reusable infrastructure blueprints
│   ├── vpc/                         ← VPC, subnets, IGW, route tables
│   ├── security/                    ← Security groups and IAM roles
│   ├── compute/                     ← EC2 instance and key pair
│   ├── alb/                         ← Application Load Balancer
│   ├── ecs/                         ← ECS Fargate cluster and service
│   ├── autoscaling/                 ← ECS auto scaling policies
│   └── remote-state/                ← Reference only — not called in main.tf
│
├── resources/                       ← Environment-specific deployments
│   ├── dev/                         ← Development environment
│   │   ├── main.tf                  ← Module calls and outputs
│   │   ├── backend.tf               ← Provider and S3 backend config
│   │   ├── variables.tf             ← Variable declarations
│   │   ├── terraform.tfvars         ← Local variable values (gitignored)
│   │   ├── terraform.tfvars.pipeline← Pipeline variable values (committed)
│   │   └── recovery-imports.sh     ← State recovery runbook script
│   │
│   └── prod/                        ← Production environment
│       ├── main.tf                  ← Identical module calls, prod values
│       ├── backend.tf               ← Prod S3 backend config
│       ├── variables.tf             ← Variable declarations
│       └── terraform.tfvars.pipeline← Pipeline variable values (committed)
│
├── apps/                            ← Application code
│   └── mecandjeo-dashboard/         ← MecanjeoOps Dashboard
│       ├── main.py                  ← FastAPI backend
│       ├── requirements.txt         ← Python dependencies
│       ├── Dockerfile               ← Multi-stage container build
│       ├── docker-compose.yml       ← Local development
│       └── static/
│           ├── index.html           ← Dashboard UI
│           ├── style.css            ← Dark theme styling
│           └── app.js               ← Frontend auto-refresh logic
│
├── .github/
│   └── workflows/
│       └── terraform-cicd.yml       ← GitHub Actions CI/CD pipeline
│
├── versions.tf                      ← Terraform and provider versions
├── .gitignore                       ← Excludes state, secrets, plan files
└── README.md                        ← This file
```

### Key Structural Principles

**Modules are environment-agnostic blueprints.** They define what can be built. The `resources/` layer defines how it is built per environment by injecting variable values. A module never knows if it is deploying to dev or prod.

**Applications live under `apps/`.** Each application has its own directory with its own Dockerfile, dependencies, and static files. The same infrastructure modules serve all applications — only the `container_image` variable changes per deployment.

**Permanent external resources.** The S3 state bucket and ECR repository live outside Terraform management — created once manually and never destroyed between sessions.

---

## 3. Prerequisites

### Required Tools

```bash
terraform -v    # Required: >= 1.10.0
aws --version   # Required: AWS CLI v2
docker -v       # Required for application phases
git --version   # Required for version control
```

### AWS Setup

```bash
# Configure AWS CLI
aws configure
# Enter: Access Key, Secret Key, us-east-1, json

# Verify authentication
aws sts get-caller-identity
```

### One-Time Manual Setup

These resources must be created once before Terraform can run:

```bash
# Create S3 state backend bucket — dev
aws s3api create-bucket \
  --bucket mecandjeo-infra-dev-tfstate \
  --region us-east-1 && \
aws s3api put-bucket-versioning \
  --bucket mecandjeo-infra-dev-tfstate \
  --versioning-configuration Status=Enabled && \
aws s3api put-bucket-encryption \
  --bucket mecandjeo-infra-dev-tfstate \
  --server-side-encryption-configuration \
  '{"Rules":[{"ApplyServerSideEncryptionByDefault":{"SSEAlgorithm":"AES256"}}]}' && \
aws s3api put-public-access-block \
  --bucket mecandjeo-infra-dev-tfstate \
  --public-access-block-configuration \
  "BlockPublicAcls=true,IgnorePublicAcls=true,\
BlockPublicPolicy=true,RestrictPublicBuckets=true"

# Create S3 state backend bucket — prod
aws s3api create-bucket \
  --bucket mecandjeo-infra-prod-tfstate \
  --region us-east-1 && \
aws s3api put-bucket-versioning \
  --bucket mecandjeo-infra-prod-tfstate \
  --versioning-configuration Status=Enabled && \
aws s3api put-bucket-encryption \
  --bucket mecandjeo-infra-prod-tfstate \
  --server-side-encryption-configuration \
  '{"Rules":[{"ApplyServerSideEncryptionByDefault":{"SSEAlgorithm":"AES256"}}]}' && \
aws s3api put-public-access-block \
  --bucket mecandjeo-infra-prod-tfstate \
  --public-access-block-configuration \
  "BlockPublicAcls=true,IgnorePublicAcls=true,\
BlockPublicPolicy=true,RestrictPublicBuckets=true"

# Create ECR repository — dev
aws ecr create-repository \
  --repository-name mecandjeo-infra-dev \
  --image-scanning-configuration scanOnPush=true \
  --region us-east-1

# Create ECR repository — prod
aws ecr create-repository \
  --repository-name mecandjeo-infra-prod \
  --image-scanning-configuration scanOnPush=true \
  --region us-east-1
```

---

## 4. Architecture

### Current Architecture — Learning Environment

```
                        INTERNET
                            │
                            ▼ HTTP port 80
                   ┌─────────────────┐
                   │ Internet Gateway│
                   └────────┬────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                    VPC — 10.0.0.0/16                        │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │               PUBLIC SUBNETS                         │   │
│  │   us-east-1a (10.0.1.0/24)  us-east-1b (10.0.2.0/24) │   │
│  │                                                      │   │
│  │   ┌─────────────────────────────────────────────┐    │   │
│  │   │         Application Load Balancer           │    │   │
│  │   │         internet-facing — port 80           │    │   │
│  │   └──────────────────┬──────────────────────────┘    │   │
│  │                      │                               │   │
│  │   ┌───────────────────▼─────────────────────────┐    │   │
│  │   │   ECS Fargate Tasks (learning — public)     │    │   │
│  │   │   mecandjeo-dashboard:SHA                   │    │   │
│  │   │   Task 1 (AZ-a)    Task 2 (AZ-b)            │    │   │
│  │   │   assign_public_ip = true (no NAT Gateway)  │    │   │
│  │   └─────────────────────────────────────────────┘    │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │               PRIVATE SUBNETS                        │   │
│  │   us-east-1a (10.0.3.0/24)  us-east-1b (10.0.4.0/24) │   │
│  │   Provisioned — ready for production workloads       │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                             │
│  EC2 t3.micro — SSH validated — Amazon Linux 2023           │
│  Security Groups — EC2 SG, ALB SG, ECS SG (chained)         │
│  IAM Role — ECS task execution — least privilege            │
└─────────────────────────────────────────────────────────────┘
                            │
            ┌───────────────▼───────────────┐
            │         Auto Scaling          │
            │   Min: 2    Max: 6 (dev)      │
            │   CPU > 70% → add task        │
            │   CPU < 30% → remove task     │
            └───────────────────────────────┘
                            │
            ┌───────────────▼───────────────┐
            │         Remote State          │
            │   S3: mecandjeo-infra-dev-    │
            │   tfstate (permanent)         │
            │   use_lockfile = true         │
            └───────────────────────────────┘

ECR:  776735193826.dkr.ecr.us-east-1.amazonaws.com/mecandjeo-infra-dev
Logs: /ecs/mecandjeo-infra-dev (CloudWatch — 7 day retention)
```

### Production Architecture — Target State

```
                        INTERNET
                            │
                   HTTPS 443│ HTTP 80 → redirect to 443
                            │
                   ┌─────────────────┐
                   │ Internet Gateway│
                   └────────┬────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                    VPC — 10.0.0.0/16                        │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │               PUBLIC SUBNETS                         │   │
│  │                                                      │   │
│  │   ALB — HTTPS — ACM Certificate — deletion_protection│   │
│  │   NAT Gateway — outbound only for private subnets    │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │               PRIVATE SUBNETS                        │   │
│  │                                                      │   │
│  │   ECS Fargate Tasks                                  │   │
│  │   assign_public_ip = false                           │   │
│  │   No direct internet access                          │   │
│  │   Pulls images via NAT Gateway                       │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
            ┌───────────────▼───────────────┐
            │         Auto Scaling          │
            │   Min: 2    Max: 10 (prod)    │
            └───────────────────────────────┘

Additional production components:
  VPC Flow Logs → CloudWatch
  AWS WAF → ALB protection
  Secrets Manager → application secrets
  CI/CD pipeline → automated deployment
```

---

## 5. Infrastructure — Stages 1-7

| Stage | What Was Built                                                 | Resources |
|-------|----------------------------------------------------------------|-----------|
| **1** | Terraform monorepo scaffold, AWS CLI setup, SSH for GitHub     | 0         |
| **2** | VPC, 4 subnets across 2 AZs, IGW, route tables                 | 12        |
| **3** | EC2 t3.micro, key pair, security group, SSH verified           | 3         |
| **4** | Dedicated security module — EC2/ALB/ECS SGs, IAM role          | 5         |
| **5** | ECR, CloudWatch logs, ECS cluster, task definition, service    | 5         |
| **6** | ALB, target group, HTTP listener — application live in browser | 3         |
| **7** | Auto scaling, S3 remote state, DynamoDB locking                | 10        |

**Total infrastructure resources: 38 → reduced to 31 after architectural improvements**

### Architectural Improvements Made

- `remote_state` module removed from Terraform — S3 bucket managed permanently outside destroy cycle
- ECR repository removed from Terraform — image preserved permanently outside destroy cycle
- `dynamodb_table` replaced with `use_lockfile = true` — simpler native S3 locking
- Terraform upgraded from 1.5.0 to 1.10.0

---

## 6. Application — Phases 1-4

| Phase | What Was Done                                                                    |
|-------|----------------------------------------------------------------------------------|
| **1** | Built FastAPI backend, HTML/CSS/JS dashboard UI, Dockerfile, docker-compose      |
| **2** | Built image locally, pushed to Docker Hub and ECR with versioned and latest tags |
| **3** | Updated Terraform config for real app — port 8000, `/health` endpoint, env vars  |
| **4** | Wired GitHub Actions pipeline — auto build, push, deploy on every push to main   |

### Application Stack

| Layer         | Technology                                          |
|---------------|-----------------------------------------------------|
| Backend       | Python 3.12 + FastAPI                               |
| Frontend      | HTML5 + CSS3 + Vanilla JavaScript                   |
| Container     | Docker multi-stage build, non-root user             |
| Registry      | Docker Hub (`s8mike/mecandjeo-dashboard`) + AWS ECR |
| Orchestration | AWS ECS Fargate                                     |
| Load Balancer | AWS Application Load Balancer                       |

### API Endpoints

| Endpoint                  | Purpose                             |
|---------------------------|-------------------------------------|
| `GET /health`             | ALB health check — must return 200  |
| `GET /api/system`         | Live CPU, memory, uptime metrics    |
| `GET /api/infrastructure` | Deployment metadata                 |
| `GET /api/services`       | Status of 7 infrastructure services |
| `GET /api/deployments`    | Deployment history timeline         |
| `GET /api/stats`          | Summary statistics                  |

---

## 7. Complete Resource Inventory

| Module      | Resource                         | Name Pattern                                |
|-------------|----------------------------------|---------------------------------------------|
| VPC         | aws_vpc                          | `{project}-{env}-vpc`                       |
| VPC         | aws_internet_gateway             | `{project}-{env}-igw`                       |
| VPC         | aws_subnet (x4)                  | `{project}-{env}-public/private-subnet-1/2` |
| VPC         | aws_route_table (x2)             | `{project}-{env}-public/private-rt`         |
| VPC         | aws_route_table_association (x4) | —                                           |
| Security    | aws_security_group (x3)          | `{project}-{env}-ec2/alb/ecs-sg`            |
| Security    | aws_iam_role                     | `{project}-{env}-ecs-task-execution-role`   |
| Security    | aws_iam_role_policy_attachment   | AmazonECSTaskExecutionRolePolicy            |
| Compute     | aws_key_pair                     | `{project}-{env}-keypair`                   |
| Compute     | aws_instance                     | `{project}-{env}-ec2`                       |
| ALB         | aws_lb                           | `{project}-{env}-alb`                       |
| ALB         | aws_lb_target_group              | `{project}-{env}-tg`                        |
| ALB         | aws_lb_listener                  | `{project}-{env}-http-listener`             |
| ECS         | aws_cloudwatch_log_group         | `/ecs/{project}-{env}`                      |
| ECS         | aws_ecs_cluster                  | `{project}-{env}-cluster`                   |
| ECS         | aws_ecs_task_definition          | `{project}-{env}-task`                      |
| ECS         | aws_ecs_service                  | `{project}-{env}-service`                   |
| Autoscaling | aws_appautoscaling_target        | ECS service                                 |
| Autoscaling | aws_appautoscaling_policy (x2)   | scale-out / scale-in                        |
| Autoscaling | aws_cloudwatch_metric_alarm (x2) | cpu-scale-out / cpu-scale-in                |

**Total: 31 managed resources per environment**

**Permanent external resources (not in Terraform state):**

| Resource       | Name                           | Why External         |
|----------------|--------------------------------|----------------------|
| S3 bucket      | `mecandjeo-infra-dev-tfstate`  | Backend prerequisite |
| S3 bucket      | `mecandjeo-infra-prod-tfstate` | Backend prerequisite |
| ECR repository | `mecandjeo-infra-dev`          | Image preservation   |
| ECR repository | `mecandjeo-infra-prod`         | Image preservation   |

---

## 8. Environment Configuration

### Dev vs Prod Comparison

| Setting                 | Dev                           | Prod                           |
|-------------------------|-------------------------------|--------------------------------|
| ECS CPU                 | 256 (0.25 vCPU)               | 512 (0.5 vCPU)                 |
| ECS Memory              | 512 MB                        | 1024 MB                        |
| EC2 type                | t3.micro                      | t3.small                       |
| Max tasks               | 6                             | 10                             |
| ALB deletion protection | false                         | true                           |
| ECS subnet placement    | public (free tier)            | private + NAT (production)     |
| HTTPS                   | No                            | Yes — ACM certificate          |
| State bucket            | `mecandjeo-infra-dev-tfstate` | `mecandjeo-infra-prod-tfstate` |

### GitHub Variables and Secrets

**Variables** (Settings → Secrets and variables → Variables):

| Variable                | Value                          |
|-------------------------|--------------------------------|
| `AWS_REGION`            | `us-east-1`                    |
| `AWS_ACCOUNT_ID`        | `776735193826`                 |
| `TF_STATE_BUCKET_DEV`   | `mecandjeo-infra-dev-tfstate`  |
| `TF_STATE_BUCKET_PROD`  | `mecandjeo-infra-prod-tfstate` |
| `DOCKERHUB_USERNAME`    | `s8mike`                       |
| `ALLOWED_SSH_CIDR_DEV`  | `YOUR_IP/32`                   |
| `ALLOWED_SSH_CIDR_PROD` | `YOUR_IP/32`                   |
| `PUBLIC_KEY`            | `ssh-ed25519 AAAA...`          |

**Secrets** (Settings → Secrets and variables → Secrets):

| Secret                  | Value                   |
|-------------------------|-------------------------|
| `AWS_ACCESS_KEY_ID`     | IAM user access key     |
| `AWS_SECRET_ACCESS_KEY` | IAM user secret key     |
| `DOCKERHUB_TOKEN`       | Docker Hub access token |

---

## 9. Session Workflow

### Every Session Start

```bash
cd resources/dev

# Confirm S3 bucket exists (create if missing — see Prerequisites)
aws s3api head-bucket --bucket mecandjeo-infra-dev-tfstate \
  && echo "Backend ready" || echo "Create bucket first"

# Confirm ECR image exists
aws ecr describe-images \
  --repository-name mecandjeo-infra-dev \
  --query "imageDetails[*].imageTags" \
  --output table

# Initialise Terraform
terraform init

# Get your current IP and update terraform.tfvars if changed
curl ifconfig.me

# Deploy
terraform plan
terraform apply

# Get the ALB DNS name — always fresh after apply
terraform output alb_dns_name
```

### Every Session End

```bash
cd resources/dev
terraform destroy
# Type yes when prompted

# Verify S3 bucket and ECR survived
aws s3api head-bucket --bucket mecandjeo-infra-dev-tfstate \
  && echo "S3 preserved" || echo "Bucket gone"
aws ecr describe-repositories \
  --repository-names mecandjeo-infra-dev \
  --query "repositories[0].repositoryName" \
  --output text
```

### What Survives Every Destroy

| Resource                  | Survives | Reason                        |
|---------------------------|----------|-------------------------------|
| S3 state bucket           | ✅       | Outside Terraform management |
| ECR repository            | ✅       | Outside Terraform management |
| ECR image                 | ✅       | Inside preserved repository  |
| Docker Hub image          | ✅       | Always safe                  |
| All application resources | ❌       | Destroyed to avoid charges   |

---

## 10. CI/CD Pipeline

### Pipeline File Location
```
.github/workflows/terraform-cicd.yml
```

### Trigger Conditions

| Event                           | Jobs That Run                            |
|---------------------------------|------------------------------------------|
| Push to `main` (relevant paths) | All 4 jobs                               |
| Pull request to `main`          | Validate only — posts plan as PR comment |
| Push to other branches          | Nothing                                  |

### Job Flow

```
validate (20s)
    │
    ▼
docker (38s)
    │
    ▼
deploy-dev (4m)
    │
    ▼ ⏸ manual approval
deploy-prod
```

### Path Filter — What Triggers the Pipeline

```yaml
paths:
  - 'apps/mecandjeo-dashboard/**'
  - 'modules/**'
  - 'resources/dev/**'
  - '.github/workflows/terraform-cicd.yml'
```

Changes to `resources/prod/`, documentation, or other files do not trigger deployment.

### Image Tagging Strategy

```
Every build produces:
  REGISTRY/REPO:SHORT_SHA    ← permanent, traceable to exact commit
  REGISTRY/REPO:latest       ← floating pointer to newest build

Short SHA = first 8 characters of git commit SHA
Example: a3f8c12d
```

---

## 11. Production Readiness

### Before First Production Deployment

Complete this checklist:

```
Infrastructure:
  ✅ Create prod S3 backend bucket manually
  ✅ Create prod ECR repository manually
  ✅ Set GitHub Variables and Secrets for prod
  ✅ Configure production GitHub Environment with required reviewers
  ⏳ Add NAT Gateway to VPC module
  ⏳ Move ECS tasks to private subnets
  ⏳ Set assign_public_ip = false in ECS module
  ⏳ Register domain in Route 53
  ⏳ Request ACM certificate for domain
  ⏳ Add HTTPS listener to ALB module
  ⏳ Add HTTP → HTTPS redirect listener
  ⏳ Set enable_deletion_protection = true on ALB
  ⏳ Enable VPC Flow Logs
  ⏳ Change ECR image_tag_mutability to IMMUTABLE

Application:
  ⏳ Build and push production image to prod ECR
  ⏳ Update container_image in prod pipeline vars
  ⏳ Add AWS Secrets Manager for app secrets
  ⏳ Configure production CloudWatch alarms and dashboard
```

### Production Code Changes Required

**Add NAT Gateway to `modules/vpc/main.tf`:**
```hcl
resource "aws_eip" "nat" {
  domain = "vpc"
}

resource "aws_nat_gateway" "main" {
  allocation_id = aws_eip.nat.id
  subnet_id     = aws_subnet.public[0].id
  depends_on    = [aws_internet_gateway.main]
}

resource "aws_route" "private_nat" {
  route_table_id         = aws_route_table.private.id
  destination_cidr_block = "0.0.0.0/0"
  nat_gateway_id         = aws_nat_gateway.main.id
}
```

**Move ECS to private subnets in `modules/ecs/main.tf`:**
```hcl
network_configuration {
  subnets          = var.private_subnet_ids
  security_groups  = [var.ecs_security_group_id]
  assign_public_ip = false
}
```

**Add HTTPS to `modules/alb/main.tf`:**
```hcl
resource "aws_lb_listener" "https" {
  load_balancer_arn = aws_lb.main.arn
  port              = 443
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS13-1-2-2021-06"
  certificate_arn   = var.acm_certificate_arn
  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.main.arn
  }
}

resource "aws_lb_listener" "http_redirect" {
  load_balancer_arn = aws_lb.main.arn
  port              = 80
  protocol          = "HTTP"
  default_action {
    type = "redirect"
    redirect {
      port        = "443"
      protocol    = "HTTPS"
      status_code = "HTTP_301"
    }
  }
}
```

---

## 12. Operational Runbook

### State Recovery — When Apply Fails with "Already Exists"

```bash
cd resources/dev
bash recovery-imports.sh
terraform plan
```

### Pre-Apply Resource Check

```bash
echo "=== Pre-Apply Check ===" && \
echo -n "Key Pair:  " && \
aws ec2 describe-key-pairs \
  --key-names mecandjeo-infra-dev-keypair \
  --query "KeyPairs[*].KeyName" \
  --output text 2>/dev/null || echo "NOT FOUND" && \
echo -n "IAM Role:  " && \
aws iam get-role \
  --role-name mecandjeo-infra-dev-ecs-task-execution-role \
  --query "Role.RoleName" \
  --output text 2>/dev/null || echo "NOT FOUND" && \
echo -n "S3 Bucket: " && \
aws s3api head-bucket \
  --bucket mecandjeo-infra-dev-tfstate 2>/dev/null \
  && echo "EXISTS (expected)" || echo "NOT FOUND — create manually" && \
echo -n "ECR Repo:  " && \
aws ecr describe-repositories \
  --repository-names mecandjeo-infra-dev \
  --query "repositories[0].repositoryName" \
  --output text 2>/dev/null || echo "NOT FOUND — create manually" && \
echo "=== Check Complete ==="
```

### ECS Task Debugging

```bash
# Check task status
aws ecs describe-services \
  --cluster mecandjeo-infra-dev-cluster \
  --services mecandjeo-infra-dev-service \
  --query "services[0].{Running:runningCount,Pending:pendingCount}" \
  --output table

# Get task failure reason
aws ecs list-tasks \
  --cluster mecandjeo-infra-dev-cluster \
  --service-name mecandjeo-infra-dev-service \
  --output text | awk '{print $2}' | xargs -I{} \
  aws ecs describe-tasks \
  --cluster mecandjeo-infra-dev-cluster \
  --tasks {} \
  --query "tasks[0].{Status:lastStatus,Reason:stoppedReason}" \
  --output table

# Check CloudWatch logs (Git Bash)
MSYS_NO_PATHCONV=1 aws logs describe-log-streams \
  --log-group-name /ecs/mecandjeo-infra-dev \
  --query "logStreams[*].logStreamName" \
  --output table
```

### Repush Image to ECR After Session

```bash
# Login
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin \
  776735193826.dkr.ecr.us-east-1.amazonaws.com

# Pull from Docker Hub if local image is gone
docker pull s8mike/mecandjeo-dashboard:v1.0.0

# Tag and push to ECR
docker tag s8mike/mecandjeo-dashboard:v1.0.0 \
  776735193826.dkr.ecr.us-east-1.amazonaws.com/mecandjeo-infra-dev:v1.0.0
docker push \
  776735193826.dkr.ecr.us-east-1.amazonaws.com/mecandjeo-infra-dev:v1.0.0
```

### Terraform Workflow Reference

```bash
cd resources/dev

terraform init                # Connect to S3 backend
terraform fmt -recursive      # Format all code
terraform validate            # Check syntax
terraform plan                # Preview changes
terraform apply               # Deploy
terraform output alb_dns_name # Get current ALB URL
terraform destroy             # Clean up — preserves S3 and ECR
terraform state list          # List managed resources
terraform state rm RESOURCE   # Remove from state without destroying
terraform import ADDR ID      # Import existing resource into state
```

---

## 13. Key Lessons Learned

### Terraform

| Lesson                                     | Detail                                                                                           |
|--------------------------------------------|--------------------------------------------------------------------------------------------------|
| State backend is a prerequisite            | S3 bucket must exist before `terraform init` — create manually and never let Terraform manage it |
| ECR images are deleted with the repository | Remove ECR from Terraform management to preserve images between sessions                         |
| `terraform state rm` vs destroy            | `state rm` removes from state only — AWS resource survives. `destroy` removes both               |
| `use_lockfile = true`                      | Replaces DynamoDB locking in Terraform 1.10+ — simpler and cheaper                               |
| Import recovery                            | When apply fails with "already exists" use `terraform import` or `recovery-imports.sh`           |
| Dependency graph                           | Terraform determines provisioning order from references — file position does not matter          |
| `prevent_destroy`                          | Protects resources from accidental deletion but orphans them if state is lost                    |

### AWS

| Lesson                           | Detail                                                                              |
|----------------------------------|-------------------------------------------------------------------------------------|
| ECS in private subnets needs NAT | Without NAT Gateway tasks cannot pull images and stay in PENDING permanently        |
| ALB DNS changes on recreate      | Always run `terraform output alb_dns_name` after apply — never reuse old DNS names  |
| Security group chaining          | Reference SG IDs not CIDR blocks for ECS inbound rules — more secure and precise    |
| IMDSv2 on Amazon Linux 2023      | Requires token-based metadata queries — use `MSYS_NO_PATHCONV=1` prefix in Git Bash |
| `t3.micro` not `t2.micro`        | Newer AWS accounts use t3.micro as the free tier eligible instance type             |
| ECR image scanning               | Enabled on push — review findings before production deployment                      |

### CI/CD

| Lesson                     | Detail                                                                                              |
|----------------------------|-----------------------------------------------------------------------------------------------------|
| Secrets vs Variables       | Use Secrets for credentials, Variables for configuration — different syntax `secrets.*` vs `vars.*` |
| Top-level `env` limitation | `vars.*` and `secrets.*` do not resolve in top-level `env` block — hardcode stable values there     |
| Never commit secrets       | GitHub push protection catches tokens in files — revoke immediately if exposed                      |
| `file()` in pipeline       | Never read local file paths in Terraform running in CI — pass as variables instead                  |
| Short SHA tags             | Use `${SHA:0:8}` for readable, traceable image tags                                                 |
| Pipeline destroy           | Always destroy manually from terminal — never automate destruction                                  |

### Git Bash on Windows

| Issue                                    | Fix                                                                |
|------------------------------------------|--------------------------------------------------------------------|
| Path conversion `/health` → Windows path | `export MSYS_NO_PATHCONV=1` in `~/.bashrc`                         |
| `python3` not found                      | Use `python` or switch to `jq` for JSON parsing                    |
| SSH URL vs HTTPS                         | Use `git@github.com:` format — more reliable than HTTPS on Windows |

---

## 14. What You Can Say in Interviews

> *"I built a production-grade AWS infrastructure from scratch using Terraform, following a monorepo pattern with reusable modules for VPC, security, compute, ECS, ALB, and auto scaling. I deployed a real Python FastAPI application containerised with Docker using a multi-stage build, pushed to both Docker Hub and AWS ECR, and deployed on ECS Fargate behind an Application Load Balancer. The entire build-push-deploy cycle is automated with a GitHub Actions pipeline that validates Terraform code, builds the Docker image, and deploys to dev automatically on every push — with a manual approval gate for production. I managed Terraform state remotely in S3 with native locking, and learned to handle real operational challenges like state drift, resource import recovery, and the chicken-and-egg backend problem."*

**Specific talking points:**

- Designed a multi-tier VPC with public and private subnets across two availability zones
- Implemented security group chaining — ECS tasks only accept traffic from the ALB security group
- Used Terraform module output chaining across six modules
- Resolved Terraform state drift using `terraform import` and a dynamic recovery script
- Separated sensitive secrets from non-sensitive configuration in GitHub Actions
- Identified and permanently resolved the S3 backend chicken-and-egg problem
- Implemented ECS auto scaling with asymmetric cooldown periods — scale out fast, scale in slow
- Pushed Docker images to two registries simultaneously with commit SHA tagging
- Diagnosed ECS task failures using AWS CLI — `CannotPullContainerError` from empty ECR

---

*Built with Terraform on AWS — Infrastructure as Code + CI/CD*
*Platform Engineering — Mecandjeo Technology — 2026*

---

Commit and push:

```bash
git add README.md
git commit -m "Final README: complete project documentation — infrastructure stages 1-7 and application phases 1-4"
git push
```

**The project is complete. 🎉** 🚀