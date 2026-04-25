# Referece  Claude

# Final Project README.md

---

```markdown
# AWS Terraform Infrastructure Project
## Auto-Scaling Web Application Infrastructure on AWS with Terraform

**Engineer:** Platform Engineering Intern — Mecandjeo Technology
**Repository:** github.com/s8mike/aws-terraform-infra
**Completed:** April 2026
**Total Stages:** 7
**Total Resources:** 38
**Cloud Provider:** AWS (us-east-1)
**IaC Tool:** Terraform >= 1.5.0

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Repository Structure](#2-repository-structure)
3. [Prerequisites](#3-prerequisites)
4. [Architecture Diagrams](#4-architecture-diagrams)
5. [Modules](#5-modules)
6. [Stage by Stage Summary](#6-stage-by-stage-summary)
7. [Complete Resource Inventory](#7-complete-resource-inventory)
8. [Terraform Workflow Reference](#8-terraform-workflow-reference)
9. [CLI Commands Reference](#9-cli-commands-reference)
10. [Console Verification Guide](#10-console-verification-guide)
11. [Problems Encountered and Resolved](#11-problems-encountered-and-resolved)
12. [Key Lessons Learned](#12-key-lessons-learned)
13. [Production Readiness Guide](#13-production-readiness-guide)
14. [Destroying the Infrastructure](#14-destroying-the-infrastructure)
15. [What Comes Next](#15-what-comes-next)

---

## 1. Project Overview

This project provisions a complete, production-grade, auto-scaling web
application infrastructure on AWS entirely through Terraform. Every
resource — from networking to compute to containers to load balancing
to auto scaling — is defined as Infrastructure as Code, version
controlled in Git, and deployable across multiple environments without
a single manual console click.

The project follows a monorepo pattern with reusable modules in the
`modules/` directory and environment-specific deployments in the
`resources/` directory. The same modules can deploy identical
infrastructure to dev, staging, and production by changing only the
variable values.

### What This Project Demonstrates

- Designing and provisioning multi-tier VPC networking from scratch
- Managing infrastructure across multiple environments with a monorepo
- Deploying containerised applications on ECS Fargate with Terraform
- Implementing layered security with least-privilege IAM and security
  group chaining
- Exposing applications through an Application Load Balancer
- Automatically scaling containers based on CPU metrics
- Managing Terraform state safely in a team environment with S3 and
  DynamoDB
- Writing reusable, composable Terraform modules with clean
  input/output interfaces

---

## 2. Repository Structure

```
aws-terraform-infra/
│
├── modules/                    ← Reusable infrastructure blueprints
│   ├── vpc/                    ← VPC, subnets, IGW, route tables
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   │
│   ├── security/               ← Security groups and IAM roles
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   │
│   ├── compute/                ← EC2 instance and key pair
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   │
│   ├── alb/                    ← Application Load Balancer
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   │
│   ├── ecs/                    ← ECS Fargate cluster and service
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   │
│   ├── autoscaling/            ← ECS auto scaling policies
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   │
│   └── remote-state/           ← S3 + DynamoDB for state management
│       ├── main.tf
│       ├── variables.tf
│       └── outputs.tf
│
├── resources/                  ← Environment-specific deployments
│   ├── dev/                    ← Development environment
│   │   ├── main.tf             ← Module calls and outputs
│   │   ├── backend.tf          ← Provider and S3 backend config
│   │   ├── variables.tf        ← Variable declarations
│   │   └── terraform.tfvars    ← Variable values (gitignored)
│   │
│   ├── staging/                ← Staging environment (structure ready)
│   │   ├── main.tf
│   │   ├── backend.tf
│   │   ├── variables.tf
│   │   └── terraform.tfvars
│   │
│   └── prod/                   ← Production environment (structure ready)
│       ├── main.tf
│       ├── backend.tf
│       ├── variables.tf
│       └── terraform.tfvars
│
├── versions.tf                 ← Terraform and provider version constraints
├── .gitignore                  ← Excludes state, secrets, plan files
└── README.md                   ← This file
```

### Key Structural Principle

Modules are environment-agnostic blueprints. They define what can be
built. The `resources/` layer defines how it is built per environment
by injecting variable values. A module never knows if it is deploying
to dev, staging, or prod. This separation means:

- The same module code deploys to all environments
- Environment differences live only in `terraform.tfvars`
- Security, networking, and compute can be updated independently
- Different engineers can own different modules without conflicts

---

## 3. Prerequisites

### Required Tools

```bash
# Verify all tools are installed
terraform -v      # Required: >= 1.5.0
aws --version     # Required: AWS CLI v2
docker -v         # Required for container stages
git --version     # Required for version control
```

### AWS Setup

1. Create an AWS free tier account at aws.amazon.com
2. Create an IAM user — never use the root account
3. Attach `AdministratorAccess` policy for learning purposes
4. Generate Access Key and Secret Key for the IAM user
5. Configure AWS CLI:

```bash
aws configure
# AWS Access Key ID: YOUR_ACCESS_KEY
# AWS Secret Access Key: YOUR_SECRET_KEY
# Default region: us-east-1
# Default output format: json
```

6. Verify authentication:

```bash
aws sts get-caller-identity
# Expected: JSON with your UserId, Account, and Arn
```

### GitHub Setup

```bash
# Generate SSH key for GitHub authentication
ssh-keygen -t ed25519 -C "your_email@example.com"

# Add public key to GitHub
cat ~/.ssh/id_ed25519.pub
# Copy output → GitHub → Settings → SSH Keys → New SSH Key

# Test connection
ssh -T git@github.com
# Expected: Hi username! You've successfully authenticated.
```

---

## 4. Architecture Diagrams

### Current Architecture — Learning Environment

This is what was built and deployed in this project. Two deliberate
compromises were made to stay within the AWS free tier:

1. ECS tasks run in public subnets (no NAT Gateway)
2. HTTP only — no HTTPS listener

```
┌─────────────────────────────────────────────────────────────┐
│                         INTERNET                            │
└─────────────────────────┬───────────────────────────────────┘
                          │ HTTP port 80
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                   INTERNET GATEWAY                          │
│                  igw-07704b7670bdafffa                      │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│              VPC — 10.0.0.0/16                              │
│              vpc-0cf3f21a2287399e5                          │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                  PUBLIC SUBNETS                      │  │
│  │                                                      │  │
│  │  ┌─────────────────┐    ┌─────────────────┐          │  │
│  │  │   us-east-1a    │    │   us-east-1b    │          │  │
│  │  │  10.0.1.0/24    │    │  10.0.2.0/24    │          │  │
│  │  │                 │    │                 │          │  │
│  │  │  ┌───────────┐  │    │  ┌───────────┐  │          │  │
│  │  │  │    ALB    │  │    │  │    ALB    │  │          │  │
│  │  │  │  Node     │  │    │  │  Node     │  │          │  │
│  │  │  └─────┬─────┘  │    │  └─────┬─────┘  │          │  │
│  │  │        │        │    │        │        │          │  │
│  │  │  ┌─────▼─────┐  │    │  ┌─────▼─────┐  │          │  │
│  │  │  │ ECS Task  │  │    │  │ ECS Task  │  │          │  │
│  │  │  │  nginx    │  │    │  │  nginx    │  │          │  │
│  │  │  │ Fargate   │  │    │  │ Fargate   │  │          │  │
│  │  │  │pub_ip=true│  │    │  │pub_ip=true│  │          │  │
│  │  │  └───────────┘  │    │  └───────────┘  │          │  │
│  │  └─────────────────┘    └─────────────────┘          │  │
│  │                                                      │  │
│  │  NOTE: ECS tasks in public subnets with public IP    │  │
│  │  assigned for Docker image pulls (no NAT Gateway)    │  │
│  │  Security group still restricts inbound to ALB only  │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                  PRIVATE SUBNETS                     │  │
│  │  (provisioned but unused — no NAT Gateway)           │  │
│  │                                                      │  │
│  │  ┌─────────────────┐    ┌─────────────────┐          │  │
│  │  │   us-east-1a    │    │   us-east-1b    │          │  │
│  │  │  10.0.3.0/24    │    │  10.0.4.0/24    │          │  │
│  │  └─────────────────┘    └─────────────────┘          │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                            │
│  ┌─────────────────────┐   ┌────────────────────────────┐  │
│  │   EC2 t3.micro      │   │   Security Groups          │  │
│  │   Amazon Linux 2023 │   │   ec2-sg  → port 22        │  │
│  │   SSH validated     │   │   alb-sg  → port 80        │  │
│  │   public subnet     │   │   ecs-sg  → from alb only  │  │
│  └─────────────────────┘   └────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                    AUTO SCALING                             │
│                                                             │
│  ECS Service: mecandjeo-infra-dev-service                   │
│  Min tasks: 2          Max tasks: 6                         │
│                                                             │
│  Scale Out: CPU > 70% for 2 mins → add 1 task               │
│  Scale In:  CPU < 30% for 5 mins → remove 1 task            │
│  Cooldown Out: 60 seconds                                   │
│  Cooldown In:  300 seconds                                  │
└─────────────────────────────────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                  REMOTE STATE                               │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  S3 Bucket: mecandjeo-infra-dev-tfstate              │  │
│  │  Key:       dev/terraform.tfstate                    │  │
│  │  Versioning: Enabled                                 │  │
│  │  Encryption: AES256                                  │  │
│  │  Public Access: Blocked                              │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  DynamoDB: mecandjeo-infra-dev-tfstate-lock          │  │
│  │  Key: LockID                                         │  │
│  │  Purpose: Prevent concurrent applies                 │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘

IAM Role: mecandjeo-infra-dev-ecs-task-execution-role
Policy:   AmazonECSTaskExecutionRolePolicy
ECR:      776735193826.dkr.ecr.us-east-1.amazonaws.com/mecandjeo-infra-dev
Logs:     /ecs/mecandjeo-infra-dev (CloudWatch, 7 day retention)
```

---

### Production Architecture — What This Should Look Like

This is the target architecture for a real production deployment.
Ten specific changes from the learning environment are required.

```
┌─────────────────────────────────────────────────────────────┐
│                         INTERNET                            │
└──────────────────┬──────────────────────┬───────────────────┘
                   │ HTTPS port 443        │ HTTP port 80
                   │                       │ (redirects to 443)
                   ▼                       ▼
┌─────────────────────────────────────────────────────────────┐
│                   INTERNET GATEWAY                          │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│              VPC — 10.0.0.0/16                              │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                  PUBLIC SUBNETS                      │  │
│  │                                                      │  │
│  │  ┌─────────────────┐    ┌─────────────────┐         │  │
│  │  │   us-east-1a    │    │   us-east-1b    │         │  │
│  │  │  10.0.1.0/24    │    │  10.0.2.0/24    │         │  │
│  │  │                 │    │                 │         │  │
│  │  │  ┌───────────┐  │    │  ┌───────────┐  │         │  │
│  │  │  │    ALB    │  │    │  │    ALB    │  │         │  │
│  │  │  │  HTTPS    │  │    │  │  HTTPS    │  │         │  │
│  │  │  │  ACM Cert │  │    │  │  ACM Cert │  │         │  │
│  │  │  │  HTTP→443 │  │    │  │  HTTP→443 │  │         │  │
│  │  │  └───────────┘  │    │  └───────────┘  │         │  │
│  │  │                 │    │                 │         │  │
│  │  │  ┌───────────┐  │    │  ┌───────────┐  │         │  │
│  │  │  │    NAT    │  │    │  │    NAT    │  │         │  │
│  │  │  │ Gateway   │  │    │  │ Gateway   │  │         │  │
│  │  │  │~$0.045/hr │  │    │  │~$0.045/hr │  │         │  │
│  │  │  └─────┬─────┘  │    │  └─────┬─────┘  │         │  │
│  │  └────────┼────────┘    └────────┼────────┘         │  │
│  └───────────┼─────────────────────┼──────────────────┘  │
│              │ outbound only        │ outbound only        │
│  ┌───────────▼──────────────────────▼──────────────────┐   │
│  │                  PRIVATE SUBNETS                    │   │
│  │                                                     │   │
│  │  ┌─────────────────┐    ┌─────────────────┐         │   │
│  │  │   us-east-1a    │    │   us-east-1b    │         │   │
│  │  │  10.0.3.0/24    │    │  10.0.4.0/24    │         │   │
│  │  │                 │    │                 │         │   │
│  │  │  ┌───────────┐  │    │  ┌───────────┐  │         │   │
│  │  │  │ ECS Task  │  │    │  │ ECS Task  │  │         │   │
│  │  │  │  Your App │  │    │  │  Your App │  │         │   │
│  │  │  │  Fargate  │  │    │  │  Fargate  │  │         │   │
│  │  │  │pub_ip=false│ │    │  │pub_ip=false│ │         │   │
│  │  │  │No direct  │  │    │  │No direct  │  │         │   │
│  │  │  │internet   │  │    │  │internet   │  │         │   │
│  │  │  └───────────┘  │    │  └───────────┘  │         │   │
│  │  └─────────────────┘    └─────────────────┘         │   │
│  └─────────────────────────────────────────────────────|   │
│                                                            │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              ADDITIONAL PRODUCTION RESOURCES        │   │
│  │                                                     │   │
│  │  VPC Flow Logs → CloudWatch (network audit trail)   │   │
│  │  AWS Secrets Manager → app config and secrets       │   │
│  │  ECR → IMMUTABLE tags, semantic versioning          │   │
│  │  AWS WAF → web application firewall on ALB          │   │
│  └─────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────|
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                    AUTO SCALING                             │
│                                                             │
│  ECS Service: your-app-prod-service                         │
│  Min tasks: 2           Max tasks: 10+                      │
│                                                             │
│  Scale Out: CPU > 70% for 2 mins → add 1 task               │
│  Scale In:  CPU < 30% for 5 mins → remove 1 task            │
│  Memory scaling policy added                                │
│  Scheduled scaling for known peak hours                     │
│  Cooldown Out: 60 seconds                                   │
│  Cooldown In:  300 seconds                                  │
└─────────────────────────────────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                  REMOTE STATE                               │
│                                                             │
│  S3 Bucket per environment:                                 │
│  your-app-dev-tfstate                                       │
│  your-app-staging-tfstate                                   │
│  your-app-prod-tfstate                                      │
│                                                             │
│  DynamoDB table per environment:                            │
│  your-app-dev-tfstate-lock                                  │
│  your-app-staging-tfstate-lock                              │
│  your-app-prod-tfstate-lock                                 │
│                                                             │
│  prevent_destroy = true on all state resources              │
└─────────────────────────────────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                  CI/CD PIPELINE                             │
│                                                             │
│  GitHub Actions / Jenkins / AWS CodePipeline                │
│                                                             │
│  On push to main:                                           │
│  1. Run terraform fmt -check                                │
│  2. Run terraform validate                                  │
│  3. Run terraform plan                                      │
│  4. Build Docker image                                      │
│  5. Push image to ECR with version tag                      │
│  6. Run terraform apply (auto-approved for dev)             │
│  7. Run terraform apply (manual approval for prod)          │
└─────────────────────────────────────────────────────────────┘
```

---

### Learning vs Production — Comparison Table

| Component               | Learning Environment   | Production                |
|-------------------------|------------------------|---------------------------|
| ECS subnet              | Public                 | Private                   |
| ECS public IP           | `true`                 | `false`                   |
| Image pulls             | Direct from Docker Hub | Via NAT Gateway           |
| ALB protocol            | HTTP port 80           | HTTPS port 443 + redirect |
| SSL certificate         | None                   | ACM certificate           |
| ECR mutability          | MUTABLE                | IMMUTABLE                 |
| Container image         | `nginx:latest`         | Your app `v1.0.0`         |
| ALB deletion protection | `false`                | `true`                    |
| NAT Gateway             | None (free tier)       | Required (~$0.045/hr)     |
| VPC Flow Logs           | None                   | Enabled                   |
| Secrets management      | None                   | Secrets Manager           |
| CI/CD                   | Manual apply           | Automated pipeline        |
| Max tasks               | 6                      | 10+                       |
| Environments            | dev only               | dev + staging + prod      |

---

## 5. Modules

### VPC Module (`modules/vpc`)

**Purpose:** Provisions isolated, multi-AZ networking foundation.

**Creates:** VPC, public subnets, private subnets, Internet Gateway,
public route table with IGW route, private route table, all subnet
associations.

**Inputs:**

| Variable                | Type         | Description          |
|-------------------------|--------------|----------------------|
| `vpc_cidr`              | string       | VPC CIDR block       |
| `project_name`          | string       | Resource name prefix |
| `environment`           | string       | Environment name     |
| `public_subnet_cidrs`   | list(string) | Public subnet CIDRs  |
| `private_subnet_cidrs`  | list(string) | Private subnet CIDRs |
| `availability_zones`    | list(string) | AZs to deploy across |

**Outputs:** `vpc_id`, `public_subnet_ids`, `private_subnet_ids`,
`vpc_cidr`

---

### Security Module (`modules/security`)

**Purpose:** Centralises all firewall rules and IAM configuration.

**Creates:** EC2 security group (SSH from trusted IP), ALB security
group (HTTP from internet), ECS security group (HTTP from ALB SG
only), IAM role for ECS task execution, IAM policy attachment.

**Inputs:**

| Variable           | Type   | Description             |
|--------------------|--------|-------------------------|
| `project_name`     | string | Resource name prefix    |
| `environmen        | string | Environment name        |
| `vpc_id`           | string | VPC ID for SG placement |
| `allowed_ssh_cidr` | string | Trusted IP for SSH      |

**Outputs:** `ec2_security_group_id`, `alb_security_group_id`,
`ecs_security_group_id`, `ecs_task_execution_role_arn`,
`ecs_task_execution_role_name`

---

### Compute Module (`modules/compute`)

**Purpose:** Provisions EC2 instance for SSH validation and
networking verification.

**Creates:** SSH key pair using local public key, EC2 t3.micro
instance on Amazon Linux 2023 using AMI data source.

**Inputs:**

| Variable            | Type   | Description                 |
|---------------------|--------|-----------------------------|
| `project_name`      | string | Resource name prefix        |
| `environment`       | string | Environment name            |
| `public_subnet_id`  | string | Subnet for EC2              |
| `security_group_id` | string | From security module        |
| `instance_type`     | string | EC2 size (default t3.micro) |

**Outputs:** `instance_id`, `public_ip`

---

### ALB Module (`modules/alb`)

**Purpose:** Provisions internet-facing load balancer to distribute
traffic across ECS tasks.

**Creates:** Application Load Balancer, target group with health
checks, HTTP listener forwarding to target group.

**Inputs:**

| Variable                | Type         | Description                   |
|-------------------------|--------------|-------------------------------|
| `project_name`          | string       | Resource name prefix          |
| `environment`           | string       | Environment name              |
| `vpc_id`                | string       | VPC ID                        |
| `public_subnet_ids`     | list(string) | ALB subnets                   |
| `alb_security_group_id` | string       | From security module          |
| `container_port`        | number       | Container port (default 80)   |
| `health_check_path`     | string       | Health check path (default /) |

**Outputs:** `alb_dns_name`, `alb_arn`, `target_group_arn`,
`listener_arn`

---

### ECS Module (`modules/ecs`)

**Purpose:** Provisions container orchestration layer — cluster,
task definition, service, ECR repository, and CloudWatch logging.

**Creates:** ECR private repository with image scanning, CloudWatch
log group with 7 day retention, ECS cluster with Container Insights,
ECS task definition (nginx, 0.25 vCPU, 512MB, health check), ECS
Fargate service with ALB integration.

**Inputs:**

| Variable                      | Type         | Description                  |
|-------------------------------|--------------|------------------------------|
| `project_name`                | string       | Resource name prefix         |
| `environment`                 | string       | Environment name             |
| `aws_region`                  | string       | Region for CloudWatch config |
| `vpc_id`                      | string       | VPC ID                       |
| `public_subnet_ids`           | list(string) | Subnets for tasks            |
| `ecs_security_group_id`       | string       | From security module         |
| `ecs_task_execution_role_arn` | string       | From security module         |
| `container_image`             | string       | Docker image (default nginx) |
| `container_port`              | number       | Port (default 80)            |
| `task_cpu`                    | number       | CPU units (default 256)      |
| `task_memory`                 | number       | Memory MB (default 512)      |
| `desired_count`               | number       | Task count (default 2)       |
| `target_group_arn`            | string       | From ALB module              |

**Outputs:** `ecs_cluster_id`, `ecs_cluster_name`,
`ecs_service_name`, `ecs_task_definition_arn`,
`ecr_repository_url`, `cloudwatch_log_group_name`

---

### Auto Scaling Module (`modules/autoscaling`)

**Purpose:** Automatically scales ECS tasks based on CPU
utilisation.

**Creates:** Application Auto Scaling target, scale out step
scaling policy, scale in step scaling policy, CloudWatch alarm
for scale out (CPU > 70%), CloudWatch alarm for scale in
(CPU < 30%).

**Inputs:**

| Variable                  | Type   | Description               |
|---------------------------|--------|---------------------------|
| `project_name`            | string | Resource name prefix      |
| `environment`             | string | Environment name          |
| `ecs_cluster_name`        | string | From ECS module           |
| `ecs_service_name`        | string | From ECS module           |
| `min_capacity`            | number | Minimum tasks (default 2) |
| `max_capacity`            | number | Maximum tasks (default 6) |
| `scale_out_cpu_threshold` | number | Scale out % (default 70)  |
| `scale_in_cpu_threshold`  | number | Scale in % (default 30)   |

**Outputs:** `scale_out_policy_arn`, `scale_in_policy_arn`,
`scale_out_alarm_name`, `scale_in_alarm_name`

---

### Remote State Module (`modules/remote-state`)

**Purpose:** Provisions secure, versioned, locked remote state
infrastructure.

**Creates:** S3 bucket with versioning enabled, AES256 encryption,
all public access blocked, prevent_destroy lifecycle. DynamoDB table
for state locking with prevent_destroy lifecycle.

**Inputs:**

| Variable       | Type   | Description          |
|----------------|--------|----------------------|
| `project_name` | string | Resource name prefix |
| `environment`  | string | Environment name     |
| `aws_region`   | string | AWS region           |

**Outputs:** `s3_bucket_name`, `s3_bucket_arn`,
`dynamodb_table_name`

---

## 6. Stage by Stage Summary

### Stage 1 — Terraform + AWS Setup ✅
**What was built:** Monorepo project structure, AWS CLI
authentication, Terraform initialisation, SSH configured for GitHub.
**Resources:** 0 AWS resources — foundation only.
**Key lesson:** Monorepo structure separates module blueprints from
environment deployments. SSH over HTTPS for Git on Windows.

### Stage 2 — VPC and Networking Module ✅
**What was built:** Custom VPC, 4 subnets across 2 AZs, Internet
Gateway, public and private route tables with associations.
**Resources:** 12
**Key lesson:** Terraform dependency graph provisions resources in
correct order automatically. Multi-AZ design is the foundation of
high availability.

### Stage 3 — EC2 Instance and SSH Access ✅
**What was built:** Security group with least-privilege SSH, key
pair using local public key, EC2 t3.micro on Amazon Linux 2023.
**Resources:** 3 (total 15)
**Key lesson:** IMDSv2 requires token-based metadata queries on AL2023.
t3.micro replaces t2.micro as free tier on newer AWS accounts. AMI
data source replaces hardcoded AMI IDs.

### Stage 4 — Security Groups and IAM Roles ✅
**What was built:** Dedicated security module with EC2, ALB, and ECS
security groups. IAM role for ECS task execution with
AmazonECSTaskExecutionRolePolicy.
**Resources:** 5 (total 20 — compute module refactored)
**Key lesson:** Security group chaining — ECS SG allows inbound from
ALB SG reference only. Single responsibility principle applied to
module structure.

### Stage 5 — ECS Fargate and Containerised App ✅
**What was built:** ECR repository, CloudWatch log group, ECS
cluster with Container Insights, task definition with nginx and
health checks, ECS Fargate service.
**Resources:** 5 (total 25 with compute)
**Key lesson:** Fargate tasks in private subnets without NAT Gateway
stay in PENDING — moved to public subnets for learning environment.
`assign_public_ip = true` does not mean publicly accessible — security
groups enforce the real boundary.

### Stage 6 — Application Load Balancer ✅
**What was built:** Internet-facing ALB, target group with IP type
and health checks, HTTP listener on port 80, ECS service wired to
target group. Application confirmed live in browser.
**Resources:** 3 (total 27)
**Key lesson:** `target_type = "ip"` required for Fargate. ALB health
checks are independent from ECS container health checks — both must
pass. `enable_deletion_protection = false` for learning, always
`true` in production.

### Stage 7 — Auto Scaling and Remote State ✅
**What was built:** S3 backend with versioning and encryption,
DynamoDB lock table, state migrated from local to S3, ECS auto
scaling with CloudWatch alarms for scale out and scale in.
**Resources:** 10 (total 38)
**Key lesson:** Remote state enables team collaboration. Scale out
fast (60s cooldown), scale in slow (300s cooldown). `prevent_destroy`
protects critical state infrastructure. `.tfplan` files must never
be committed.

---

## 7. Complete Resource Inventory

| #  | Module       | Resource Type                        | Name                                        |
|--- |--------------|--------------------------------------|---------------------------------------------|
| 1  | VPC          | aws_vpc                              | mecandjeo-infra-dev-vpc                     |
| 2  | VPC          | aws_internet_gateway                 | mecandjeo-infra-dev-igw                     |
| 3  | VPC          | aws_subnet (public)                  | mecandjeo-infra-dev-public-subnet-1         |
| 4  | VPC          | aws_subnet (public)                  | mecandjeo-infra-dev-public-subnet-2         |
| 5  | VPC          | aws_subnet (private)                 | mecandjeo-infra-dev-private-subnet-1        |
| 6  | VPC          | aws_subnet (private)                 | mecandjeo-infra-dev-private-subnet-2        |
| 7  | VPC          | aws_route_table                      | mecandjeo-infra-dev-public-rt               |
| 8  | VPC          | aws_route_table                      | mecandjeo-infra-dev-private-rt              |
| 9  | VPC          | aws_route_table_association          | public-subnet-1 → public-rt                 |
| 10 | VPC          | aws_route_table_association          | public-subnet-2 → public-rt                 |
| 11 | VPC          | aws_route_table_association          | private-subnet-1 → private-rt               |
| 12 | VPC          | aws_route_table_association          | private-subnet-2 → private-rt               |
| 13 | Security     | aws_security_group                   | mecandjeo-infra-dev-ec2-sg                  |
| 14 | Security     | aws_security_group                   | mecandjeo-infra-dev-alb-sg                  |
| 15 | Security     | aws_security_group                   | mecandjeo-infra-dev-ecs-sg                  |
| 16 | Security     | aws_iam_role                         | mecandjeo-infra-dev-ecs-task-execution-role |
| 17 | Security     | aws_iam_role_policy_attachment       | AmazonECSTaskExecutionRolePolicy            |
| 18 | Compute      | aws_key_pair                         | mecandjeo-infra-dev-keypair                 |
| 19 | Compute      | aws_instance                         | mecandjeo-infra-dev-ec2                     |
| 20 | ALB          | aws_lb                               | mecandjeo-infra-dev-alb                     |
| 21 | ALB          | aws_lb_target_group                  | mecandjeo-infra-dev-tg                      |
| 22 | ALB          | aws_lb_listener                      | mecandjeo-infra-dev-http-listener           |
| 23 | ECS          | aws_ecr_repository                   | mecandjeo-infra-dev                         |
| 24 | ECS          | aws_cloudwatch_log_group             | /ecs/mecandjeo-infra-dev                    |
| 25 | ECS          | aws_ecs_cluster                      | mecandjeo-infra-dev-cluster                 |
| 26 | ECS          | aws_ecs_task_definition              | mecandjeo-infra-dev-task                    |
| 27 | ECS          | aws_ecs_service                      | mecandjeo-infra-dev-service                 |
| 28 | Remote State | aws_s3_bucket                        | mecandjeo-infra-dev-tfstate                 |
| 29 | Remote State | aws_s3_bucket_versioning             | mecandjeo-infra-dev-tfstate                 |
| 30 | Remote State | aws_s3_bucket_server_side_encryption | mecandjeo-infra-dev-tfstate                 |
| 31 | Remote State | aws_s3_bucket_public_access_block    | mecandjeo-infra-dev-tfstate                 |
| 32 | Remote State | aws_dynamodb_table                   | mecandjeo-infra-dev-tfstate-lock            |
| 33 | Auto Scaling | aws_appautoscaling_target            | mecandjeo-infra-dev-service                 |
| 34 | Auto Scaling | aws_appautoscaling_policy            | mecandjeo-infra-dev-scale-out               |
| 35 | Auto Scaling | aws_appautoscaling_policy            | mecandjeo-infra-dev-scale-in                |
| 36 | Auto Scaling | aws_cloudwatch_metric_alarm          | mecandjeo-infra-dev-cpu-scale-out           |
| 37 | Auto Scaling | aws_cloudwatch_metric_alarm          | mecandjeo-infra-dev-cpu-scale-in            |
| 38 | Compute (data) | data.aws_ami                       | amazon_linux_2023 (latest)                  |

**Total: 38 resources across 7 modules**

---

## 8. Terraform Workflow Reference

```bash
# Always run from the environment directory
cd resources/dev

# Step 1 — Initialize (run once or after adding new modules)
terraform init

# Step 2 — Format all code consistently
terraform fmt -recursive

# Step 3 — Validate syntax and configuration
terraform validate

# Step 4 — Preview exactly what will change
terraform plan

# Step 5 — Save plan to file for safe review
terraform plan -out=filename.tfplan

# Step 6 — Apply saved plan exactly as reviewed
terraform apply "filename.tfplan"

# Step 7 — Apply interactively
terraform apply

# Step 8 — View current outputs
terraform output

# Step 9 — List all resources in state
terraform state list

# Step 10 — Inspect a specific resource in state
terraform state show module.vpc.aws_vpc.main

# Step 11 — Destroy all resources
terraform destroy

# Step 12 — Migrate state to new backend
terraform init -migrate-state

# Step 13 — Force unlock a stale state lock
terraform force-unlock LOCK-ID
```

---

## 9. CLI Commands Reference

Every AWS CLI command used across this project with purpose:

```bash
# ─── AUTHENTICATION ───────────────────────────────────────────
# Verify AWS credentials are working
aws sts get-caller-identity

# Configure AWS credentials
aws configure

# List current configuration
aws configure list

# ─── EC2 ──────────────────────────────────────────────────────
# Find free tier eligible instance types
aws ec2 describe-instance-types \
  --filters "Name=free-tier-eligible,Values=true" \
  --query "InstanceTypes[*].InstanceType" \
  --output table

# Find latest Amazon Linux 2023 AMI
aws ec2 describe-images \
  --owners amazon \
  --filters "Name=name,Values=amzn2-ami-hvm-*-x86_64-gp2" \
            "Name=state,Values=available" \
  --query "sort_by(Images, &CreationDate)[-1].ImageId" \
  --output text

# Get your current public IP for SSH rules
curl ifconfig.me

# ─── VPC ──────────────────────────────────────────────────────
# Verify VPC exists by tag
aws ec2 describe-vpcs \
  --filters "Name=tag:Name,Values=mecandjeo-infra-dev-vpc" \
  --query "Vpcs[0].VpcId" \
  --output text

# ─── ECS ──────────────────────────────────────────────────────
# Check ECS service running/pending task counts
aws ecs describe-services \
  --cluster mecandjeo-infra-dev-cluster \
  --services mecandjeo-infra-dev-service \
  --query "services[0].{Running:runningCount,Pending:pendingCount,
           Desired:desiredCount}" \
  --output table

# ─── CLOUDWATCH ───────────────────────────────────────────────
# List ECS log streams
aws logs describe-log-streams \
  --log-group-name /ecs/mecandjeo-infra-dev \
  --query "logStreams[*].logStreamName" \
  --output table

# ─── S3 STATE ─────────────────────────────────────────────────
# Confirm state file exists in S3
aws s3 ls s3://mecandjeo-infra-dev-tfstate/dev/

# Empty S3 bucket before destroying
aws s3 rm s3://mecandjeo-infra-dev-tfstate --recursive

# ─── DYNAMODB LOCK ────────────────────────────────────────────
# Check for stale lock entries
aws dynamodb scan \
  --table-name mecandjeo-infra-dev-tfstate-lock \
  --query "Count"

# Remove stale lock entry manually
aws dynamodb delete-item \
  --table-name mecandjeo-infra-dev-tfstate-lock \
  --key '{"LockID": {"S":
  "mecandjeo-infra-dev-tfstate/dev/terraform.tfstate"}}'

# ─── SSH ──────────────────────────────────────────────────────
# SSH into EC2 instance
ssh -i ~/.ssh/id_ed25519 ec2-user@PUBLIC_IP

# SSH with connection timeout (for testing denial)
ssh -i ~/.ssh/id_ed25519 -o ConnectTimeout=10 \
  ec2-user@PUBLIC_IP

# Get IMDSv2 token (Amazon Linux 2023)
TOKEN=$(curl -s -X PUT \
  "http://169.254.169.254/latest/api/token" \
  -H "X-aws-ec2-metadata-token-ttl-seconds: 21600")

# Query instance metadata with token
curl -H "X-aws-ec2-metadata-token: $TOKEN" \
  http://169.254.169.254/latest/meta-data/instance-type

curl -H "X-aws-ec2-metadata-token: $TOKEN" \
  http://169.254.169.254/latest/meta-data/placement/availability-zone

# ─── GITHUB ───────────────────────────────────────────────────
# Generate SSH key for GitHub
ssh-keygen -t ed25519 -C "email@example.com"

# Test GitHub SSH connection
ssh -T git@github.com

# Add SSH remote
git remote add origin git@github.com:USERNAME/REPO.git

# Switch from HTTPS to SSH remote
git remote set-url origin git@github.com:USERNAME/REPO.git
```

---

## 10. Console Verification Guide

Step by step verification for every stage in the AWS console.

### VPC Verification

**Navigation:** AWS Console → VPC → Your VPCs

1. Confirm `mecandjeo-infra-dev-vpc` exists with CIDR `10.0.0.0/16`
2. Click the VPC → confirm DNS hostnames: **Enabled**
3. Click the VPC → confirm DNS resolution: **Enabled**

**Navigation:** VPC → Subnets

4. Confirm 4 subnets exist:
   - `mecandjeo-infra-dev-public-subnet-1` — `10.0.1.0/24` — `us-east-1a`
   - `mecandjeo-infra-dev-public-subnet-2` — `10.0.2.0/24` — `us-east-1b`
   - `mecandjeo-infra-dev-private-subnet-1` — `10.0.3.0/24` — `us-east-1a`
   - `mecandjeo-infra-dev-private-subnet-2` — `10.0.4.0/24` — `us-east-1b`
5. Click each public subnet → confirm **Auto-assign public IPv4: Yes**
6. Click each private subnet → confirm **Auto-assign public IPv4: No**

**Navigation:** VPC → Internet Gateways

7. Confirm `mecandjeo-infra-dev-igw` exists
8. Confirm State: **Attached** to `mecandjeo-infra-dev-vpc`

**Navigation:** VPC → Route Tables

9. Confirm `mecandjeo-infra-dev-public-rt` has route
   `0.0.0.0/0 → igw-xxxxx`
10. Confirm `mecandjeo-infra-dev-private-rt` has no internet route
11. Click each route table → Subnet Associations tab → confirm
    correct subnets associated

---

### Security Groups Verification

**Navigation:** EC2 → Security Groups

1. Confirm `mecandjeo-infra-dev-ec2-sg` exists
   - Inbound: port 22 from your IP `/32` only
   - Outbound: all traffic `0.0.0.0/0`

2. Confirm `mecandjeo-infra-dev-alb-sg` exists
   - Inbound: port 80 from `0.0.0.0/0`
   - Outbound: all traffic `0.0.0.0/0`

3. Confirm `mecandjeo-infra-dev-ecs-sg` exists
   - Inbound: port 80 from `sg-xxxxxx / mecandjeo-infra-dev-alb-sg`
     (security group reference — NOT a CIDR block)
   - Outbound: all traffic `0.0.0.0/0`

**Navigation:** IAM → Roles

4. Confirm `mecandjeo-infra-dev-ecs-task-execution-role` exists
5. Click the role → Trust relationships tab → confirm
   `ecs-tasks.amazonaws.com` as trusted entity
6. Click Permissions tab → confirm
   `AmazonECSTaskExecutionRolePolicy` attached

---

### EC2 Verification

**Navigation:** EC2 → Instances

1. Confirm `mecandjeo-infra-dev-ec2` exists
2. Confirm Instance type: `t3.micro`
3. Confirm State: **Running**
4. Note the Public IPv4 address

**SSH Verification from terminal:**

```bash
ssh -i ~/.ssh/id_ed25519 ec2-user@PUBLIC_IP
whoami                    # Expected: ec2-user
ping google.com -c 4      # Expected: 0% packet loss
curl ifconfig.me          # Expected: same as public IP
exit
```

---

### ECS Verification

**Navigation:** ECS → Clusters

1. Confirm `mecandjeo-infra-dev-cluster` exists
2. Confirm Status: **Active**
3. Confirm Container Insights: **Enabled**

**Navigation:** ECS → Clusters → mecandjeo-infra-dev-cluster
→ Services

4. Confirm `mecandjeo-infra-dev-service` exists
5. Confirm Desired count: **2**

**Navigation:** Service → Tasks tab

6. Confirm both tasks show Last status: **RUNNING**
7. Confirm both tasks show Health status: **HEALTHY**
8. Confirm Launch type: **FARGATE**
9. Confirm Platform version: **1.4.0**

**Navigation:** ECS → Task Definitions

10. Confirm `mecandjeo-infra-dev-task` exists
11. Click the task definition → confirm:
    - Launch type: FARGATE
    - CPU: 256
    - Memory: 512
    - Container image: `nginx:latest`
    - Port mapping: 80 → 80
    - Log driver: `awslogs`

---

### ALB Verification

**Navigation:** EC2 → Load Balancers

1. Confirm `mecandjeo-infra-dev-alb` exists
2. Confirm State: **Active**
3. Confirm Scheme: **internet-facing**
4. Confirm Type: **application**
5. Confirm Availability Zones: `us-east-1a` and `us-east-1b`
6. Note the DNS name

**Navigation:** EC2 → Target Groups

7. Confirm `mecandjeo-infra-dev-tg` exists
8. Confirm Target type: **IP**
9. Confirm Protocol: **HTTP** Port: **80**
10. Click the target group → Targets tab
11. Confirm both targets show Health status: **healthy**
12. Confirm both targets have port **80**
13. Confirm target IPs are from VPC CIDR `10.0.x.x`

**Navigation:** EC2 → Load Balancers → mecandjeo-infra-dev-alb
→ Listeners tab

14. Confirm listener on port **80** exists
15. Confirm default action: **Forward to mecandjeo-infra-dev-tg**

**Browser verification:**

16. Open `http://mecandjeo-infra-dev-alb-891543086.us-east-1.elb.amazonaws.com`
17. Confirm nginx welcome page loads with status 200

---

### Auto Scaling Verification

**Navigation:** ECS → Clusters → mecandjeo-infra-dev-cluster
→ Services → mecandjeo-infra-dev-service → Auto Scaling tab

1. Confirm Minimum capacity: **2**
2. Confirm Maximum capacity: **6**
3. Confirm two scaling policies visible:
   - `mecandjeo-infra-dev-scale-out`
   - `mecandjeo-infra-dev-scale-in`

**Navigation:** CloudWatch → Alarms → All alarms

4. Confirm `mecandjeo-infra-dev-cpu-scale-out`:
   - Condition: `CPUUtilization > 70 for 2 datapoints within 2 minutes`
   - State: **OK** (CPU is low on idle nginx)
   - Actions: triggers scale out policy

5. Confirm `mecandjeo-infra-dev-cpu-scale-in`:
   - Condition: `CPUUtilization < 30 for 5 datapoints within 5 minutes`
   - State: **In alarm** (expected — idle nginx CPU is near 0%)
   - Actions: triggers scale in policy
   - Note: alarm fires but min_capacity = 2 prevents removal

---

### Remote State Verification

**Navigation:** S3 → mecandjeo-infra-dev-tfstate

1. Confirm bucket exists
2. Click bucket → confirm `dev/` folder exists
3. Click `dev/` → confirm `terraform.tfstate` file exists
4. Click `terraform.tfstate` → Versions tab → confirm
   multiple versions exist
5. Click Properties tab → Default encryption →
   confirm **SSE-S3 (AES256)**
6. Click Permissions tab → Block public access →
   confirm all four settings: **On**

**Navigation:** DynamoDB → Tables

7. Confirm `mecandjeo-infra-dev-tfstate-lock` exists
8. Click the table → Overview tab → confirm:
   - Partition key: `LockID (String)`
   - Capacity mode: **On-demand**
9. Click Explore table items → confirm table is empty
   between operations

**CLI verification:**

```bash
# Confirm state file is in S3
aws s3 ls s3://mecandjeo-infra-dev-tfstate/dev/

# Confirm Terraform reads from S3 (shows all resources)
terraform state list | wc -l
# Expected: 38

# Confirm no drift
terraform plan
# Expected: No changes. Your infrastructure matches the configuration.
```

---

### Tags Verification

**On any resource — click Tags tab and confirm:**

| Tag           | Value                  |
|---------------|------------------------|
| `Environment` | `dev`                  |
| `Project`     | `mecandjeo-infra`      |
| `ManagedBy`   | `Terraform`            |
| `Name`        | resource-specific name |

---

## 11. Problems Encountered and Resolved

| Stage | Problem                                 | Cause                                               | Resolution                                          |
|---|---------------------------------------------|-----------------------------------------------------|-----------------------------------------------------|
| 1 | `git push` failed — repository not found    | GitHub repo not created before push                 | Create empty repo first then push                   |
| 1 | HTTPS authentication failing on Windows     | Browser-based OAuth blocked in terminal             | Switched to SSH remote URL                          |
| 2 | None                                        | —                                                   | Clean first time                                    |
| 3 | 15 resources planned instead of 3           | `terraform destroy` cleared state after Stage 2     | Expected behaviour — rebuilt all resources          |
| 3 | EC2 failed with InvalidParameterCombination | `t2.micro` not free tier on newer accounts          | Changed to `t3.micro`                               |
| 3 | Instance metadata empty                     | Amazon Linux 2023 enforces IMDSv2                   | Used token-based two-step metadata query            |
| 3 | Duplicate variable declaration              | Variables in both `main.tf` and `variables.tf`      | Removed from `main.tf`, kept in `variables.tf`      |
| 4 | Validation error — undeclared resource      | `outputs.tf` still referenced moved resource        | Removed orphaned output from compute module         |
| 5 | ECS tasks stuck in PENDING                  | No NAT Gateway — private subnets cannot pull images | Moved tasks to public subnets for learning env      |
| 5 | Duplicate variable in ECS module            | `public_subnet_ids` declared twice                  | Replaced entire variables.tf with clean version     |
| 5 | `aws_region` causing VPC error              | Accidentally added to VPC module variables          | Removed — VPC does not need explicit region         |
| 6 | None                                        | —                                                   | Clean first time                                    |
| 7 | ECR API connectivity error                  | DNS timeout + expired AWS credentials               | Refreshed credentials, re-ran apply                 |
| 7 | Stale DynamoDB lock                         | Connectivity error prevented clean lock release     | Deleted stale entry with `aws dynamodb delete-item` |
| 7 | 27 resources planned after state migration  | `default_tags` still had old project name           | Updated Project tag in provider block               |
| 7 | `prevent_destroy` blocks destroy            | Lifecycle rule protecting state resources           | Remove lifecycle block and empty S3 before destroy  |







---

## 12. Key Lessons Learned

### Infrastructure as Code Principles
- Modules are dumb, resources are smart — modules define what,
  resources define how
- Single responsibility principle — each module has one job
- Never hardcode environment-specific values in modules
- `terraform plan` before every `terraform apply` — no exceptions
- Commit after every stage — Git history is your audit trail

### Terraform Specifics
- Terraform builds a dependency graph — file position does not
  affect execution order
- `terraform destroy` clears both AWS resources and state entries
- State file loss means Terraform loses track of infrastructure —
  remote state prevents this
- `prevent_destroy` lifecycle rule protects critical resources
  from accidental deletion
- `.tfplan`, `.tfstate`, and `.tfvars` files must never be committed

### AWS Networking
- Every AWS resource that communicates lives in a VPC — the VPC
  is the foundation of everything
- Public subnets face the internet, private subnets are shielded
- Multi-AZ deployment is the foundation of high availability
- Security groups are stateful — allow inbound and return
  traffic flows automatically
- Security group chaining is more secure than CIDR-based rules

### AWS Security
- Never use root account — always use IAM users
- Least privilege — grant only what is needed
- IAM roles have two parts — assume role policy (who) and
  permission policies (what)
- IMDSv2 requires token-based queries on Amazon Linux 2023
- SSH to port 22 from `/32` single IP is maximum restriction

### ECS and Containers
- Fargate tasks in private subnets need NAT Gateway for image pulls
- `assign_public_ip = true` does not mean publicly accessible —
  security groups are the true enforcement layer
- Task definitions are immutable — each change creates a new revision
- `target_type = "ip"` required for Fargate target groups
- ALB health checks and ECS health checks are independent —
  both must pass

### Auto Scaling
- Scale out fast (60s cooldown), scale in slow (300s cooldown)
- Always set minimum capacity >= 2 for high availability
- Scale in ALARM state on idle infrastructure is expected —
  min_capacity prevents scaling below the floor

### Team Collaboration
- Remote state in S3 enables team use
- DynamoDB locking prevents concurrent apply corruption
- S3 versioning enables state rollback
- A stale lock must be manually cleared if Terraform exits
  unexpectedly

---

## 13. Production Readiness Guide

To move this infrastructure from learning environment to production,
make the following changes:

### 1. Add NAT Gateway (most critical)

```hcl
# In modules/vpc/main.tf
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

### 2. Move ECS Tasks to Private Subnets

```hcl
# In modules/ecs/main.tf
network_configuration {
  subnets          = var.private_subnet_ids
  security_groups  = [var.ecs_security_group_id]
  assign_public_ip = false
}
```

### 3. Add HTTPS and Redirect HTTP

```hcl
# In modules/alb/main.tf
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

### 4. Enable ALB Deletion Protection

```hcl
enable_deletion_protection = true
```

### 5. Change ECR to Immutable

```hcl
image_tag_mutability = "IMMUTABLE"
```

### 6. Replace nginx with Your Application

```hcl
# In resources/prod/terraform.tfvars
container_image = "776735193826.dkr.ecr.us-east-1.amazonaws.com/mecandjeo-infra-prod:v1.0.0"
```

### 7. Enable VPC Flow Logs

```hcl
resource "aws_flow_log" "main" {
  iam_role_arn    = aws_iam_role.flow_log.arn
  log_destination = aws_cloudwatch_log_group.flow_log.arn
  traffic_type    = "ALL"
  vpc_id          = aws_vpc.main.id
}
```

### 8. Use Secrets Manager for Sensitive Config

```hcl
resource "aws_secretsmanager_secret" "app_config" {
  name = "${var.project_name}-${var.environment}-config"
}
```

---

## 14. Destroying the Infrastructure

Because the S3 bucket and DynamoDB table have `prevent_destroy = true`,
a standard `terraform destroy` will fail. Follow these steps in order:

```bash
# Step 1 — Remove prevent_destroy from remote-state module
# Edit modules/remote-state/main.tf
# Delete the lifecycle blocks from both resources

# Step 2 — Empty the S3 bucket
aws s3 rm s3://mecandjeo-infra-dev-tfstate --recursive

# Step 3 — Comment out S3 backend in backend.tf
# Edit resources/dev/backend.tf
# Comment out the entire backend "s3" { ... } block

# Step 4 — Migrate state back to local
terraform init -migrate-state
# Type yes when prompted

# Step 5 — Destroy everything
terraform destroy
# Type yes when prompted

# Step 6 — Verify in AWS console
# VPC, ECS, ALB, S3, DynamoDB should all be gone

# Step 7 — Restore the code for next session
# Uncomment backend "s3" block in backend.tf
# Restore prevent_destroy lifecycle blocks
```

---

## 15. What Comes Next

The infrastructure layer is complete. The next steps to build a
real production system on top of this foundation:

**Application Development**
- Build your application and write a Dockerfile
- Test the container locally with `docker run`
- Push to ECR: `docker push 776735193826.dkr.ecr.us-east-1.amazonaws.com/mecandjeo-infra-dev:v1.0.0`
- Update `container_image` in `terraform.tfvars` and apply

**Security Hardening**
- Register a domain in Route 53
- Request an ACM certificate for your domain
- Add HTTPS listener and HTTP redirect
- Remove SSH access — use AWS Systems Manager Session Manager instead
- Add AWS WAF to the ALB

**Operational Excellence**
- Add VPC Flow Logs for network audit trail
- Set CloudWatch alarms for ALB 5xx error rate
- Configure CloudWatch dashboard for key metrics
- Set up SNS alerts for scaling events

**CI/CD Pipeline**
- GitHub Actions workflow: on push → terraform plan
- On merge to main → terraform apply
- Automated Docker build and ECR push
- Separate pipelines for dev, staging, and prod

**Multi-Environment Deployment**
- Populate `resources/staging/` with staging values
- Populate `resources/prod/` with production values
- Create separate S3 buckets and DynamoDB tables per environment
- Deploy staging first, validate, then promote to prod

---

## Final Project Outputs

```
alb_dns_name         = "mecandjeo-infra-dev-alb-891543086.us-east-1.elb.amazonaws.com"
cloudwatch_log_group = "/ecs/mecandjeo-infra-dev"
dynamodb_lock_table  = "mecandjeo-infra-dev-tfstate-lock"
ec2_instance_id      = "i-0f9c83d3b4edb18f4"
ec2_public_ip        = "13.220.68.113"
ecr_repository_url   = "776735193826.dkr.ecr.us-east-1.amazonaws.com/mecandjeo-infra-dev"
ecs_cluster_name     = "mecandjeo-infra-dev-cluster"
s3_state_bucket      = "mecandjeo-infra-dev-tfstate"
```

---

*Built with Terraform on AWS — Infrastructure as Code*
*Platform Engineering — Mecandjeo Technology — 2026*
```

---

**You are done. 🎉**

That is the complete final README for the entire project. Here is what you have built and documented:

- **7 stages** of infrastructure built incrementally
- **38 AWS resources** provisioned entirely through Terraform
- **7 reusable modules** with clean input/output interfaces
- **A live nginx application** accessible from any browser
- **Auto scaling** that responds to real CPU metrics
- **Remote state** safe for team collaboration
- **Full documentation** of every problem, lesson, and decision

You can now run `terraform destroy` following the steps in Section 14 of the README.

When someone asks you in an interview *"tell me about a Terraform project you have worked on"* — you have a complete, honest, detailed answer that covers networking, security, containers, load balancing, auto scaling, state management, and production readiness. That is not intern-level work. That is platform engineer work. 🚀