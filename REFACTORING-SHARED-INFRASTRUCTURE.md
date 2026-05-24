
---

Now the `REFACTORING-SHARED-INFRASTRUCTURE.md`:

---

**File: `REFACTORING-SHARED-INFRASTRUCTURE.md`**

```markdown
# Shared Infrastructure Refactoring
## MecanjeoOps — Multi-Application Platform
**Mecandjeo Technology — Platform Engineering — 2026**

---

## Overview

This document covers the complete refactoring of the
MecanjeoOps infrastructure from a tightly coupled
single-state architecture to a fully decoupled
shared infrastructure pattern. After this refactoring
every application deploys and destroys independently
with zero dependency on any other application.

---

## Why This Refactoring Was Done

### Before — Tightly Coupled

```
resources/dev/
  └── main.tf contains:
      ├── VPC, subnets, IGW, route tables    ← free
      ├── Security groups, IAM roles         ← free
      ├── EC2 instance                       ← free tier
      └── Dashboard ALB, ECS, autoscaling    ← costs money

resources/portfolio/dev/
  └── reads outputs from dashboard state
      └── portfolio DEPENDS ON dashboard being deployed
```

**Problems with this approach:**

| Problem                                 | Impact                                       |
|-----------------------------------------|----------------------------------------------|
| Dashboard and portfolio tightly coupled | Deploy dashboard just to deploy portfolio    |
| Destroy dashboard destroys shared infra | Portfolio breaks immediately                 |
| All 31 resources deploy every session   | ~5 minutes per session start                 |
| New app always depends on dashboard     | Fragile dependency chain                     |
| School app in separate repo             | Different modules, different patterns, drift |

### After — Fully Decoupled

```
resources/shared/dev/
  └── VPC, security, IAM, EC2 — FREE — always running

resources/dashboard/dev/
  └── ALB, ECS, autoscaling — reads from shared state

resources/portfolio/dev/
  └── ALB, ECS, autoscaling — reads from shared state

resources/school/dev/
  └── ALB, ECS, autoscaling — reads from shared state
```

**Benefits:**

| Benefit                                    | Impact                         |
|--------------------------------------------|--------------------------------|
| Shared infra runs permanently at zero cost | No rebuild every session       |
| Each app deploys independently             | 12 resources in ~2 minutes     |
| No app depends on another                  | Destroy any app safely         |
| All apps use same modules                  | Consistent pattern, no drift   |
| School app integrated into monorepo        | One repo, one pipeline pattern |

---

## New Directory Structure

```
aws-terraform-infra/
│
├── modules/                         ← unchanged — shared blueprints
│   ├── vpc/
│   ├── security/                    ← updated: dynamic ports, task role
│   ├── compute/
│   ├── alb/
│   ├── ecs/                         ← updated: force deployment config
│   └── autoscaling/
│
├── resources/
│   ├── shared/
│   │   └── dev/
│   │       ├── main.tf              ← VPC, security, IAM, EC2 only
│   │       ├── backend.tf           ← key: mecandjeo-shared/dev/
│   │       ├── variables.tf
│   │       └── terraform.tfvars.pipeline
│   │
│   ├── dashboard/
│   │   └── dev/
│   │       ├── main.tf              ← ALB, ECS, autoscaling only
│   │       ├── backend.tf           ← key: mecandjeo-dashboard/dev/
│   │       ├── variables.tf
│   │       └── terraform.tfvars.pipeline
│   │
│   ├── portfolio/
│   │   └── dev/
│   │       ├── main.tf              ← ALB, ECS, autoscaling only
│   │       ├── backend.tf           ← key: mecandjeo-portfolio/dev/
│   │       ├── variables.tf
│   │       └── terraform.tfvars.pipeline
│   │
│   ├── school/
│   │   └── dev/
│   │       ├── main.tf              ← ALB, ECS, autoscaling only
│   │       ├── backend.tf           ← key: mecandjeo-school/dev/
│   │       ├── variables.tf
│   │       └── terraform.tfvars.pipeline
│   │
│   └── prod/                        ← unchanged — future use
│
└── apps/
    ├── mecandjeo-dashboard/         ← unchanged
    ├── mecandjeo-portfolio/         ← unchanged
    └── mecandjeo-school/            ← NEW — integrated from separate repo
```

---

## New S3 State Structure

```
mecandjeo-infra-dev-tfstate/
├── mecandjeo-shared/dev/terraform.tfstate      ← 21 resources — permanent
├── mecandjeo-dashboard/dev/terraform.tfstate   ← 12 resources — per session
├── mecandjeo-portfolio/dev/terraform.tfstate   ← 12 resources — per session
└── mecandjeo-school/dev/terraform.tfstate      ← 12 resources — per session
```

### State Key Convention

```
{application-name}/{environment}/terraform.tfstate

mecandjeo-shared/dev/terraform.tfstate
mecandjeo-dashboard/dev/terraform.tfstate
mecandjeo-portfolio/dev/terraform.tfstate
mecandjeo-school/dev/terraform.tfstate
mecandjeo-banking/dev/terraform.tfstate     ← future
```

---

## How terraform_remote_state Works

Every application reads shared infrastructure values
from the shared state file via `terraform_remote_state`.
No values are passed as variables — they are read
internally from S3 state.

```hcl
# In every app's main.tf
data "terraform_remote_state" "shared" {
  backend = "s3"
  config = {
    bucket = "mecandjeo-infra-dev-tfstate"
    key    = "mecandjeo-shared/dev/terraform.tfstate"
    region = "us-east-1"
  }
}

locals {
  vpc_id                      = data.terraform_remote_state.shared.outputs.vpc_id
  public_subnet_ids           = data.terraform_remote_state.shared.outputs.public_subnet_ids
  alb_security_group_id       = data.terraform_remote_state.shared.outputs.alb_security_group_id
  ecs_security_group_id       = data.terraform_remote_state.shared.outputs.ecs_security_group_id
  ecs_task_execution_role_arn = data.terraform_remote_state.shared.outputs.ecs_task_execution_role_arn
}
```

### Dependency Chain

```
Shared must deploy first → writes outputs to S3
        ↓
Any app can deploy independently → reads outputs from S3
        ↓
Any app can destroy independently → shared unaffected
        ↓
Shared destroys last → only when all apps are gone
```

---

## Resource Count Per State

| State     | Resources | Contains                         | Cost       |
|-----------|-----------|----------------------------------|------------|
| Shared    | 21        | VPC x12, Security x7, Compute x2 | Free       |
| Dashboard | 12        | ALB x3, ECS x4, Autoscaling x5   | ~$0.016/hr |
| Portfolio | 12        | ALB x3, ECS x4, Autoscaling x5   | ~$0.012/hr |
| School    | 12        | ALB x3, ECS x4, Autoscaling x5   | ~$0.004/hr |

---

## Security Module Changes

### 1. Dynamic Port Block

Replaced single `container_port` variable with a
`dynamic` ingress block driven by `app_ports` list.
Adding a new application only requires adding its
port to the list.

```hcl
locals {
  all_traffic_cidr = "0.0.0.0/0"
  # Add new app port here when adding a new application
  app_ports = [8000, 8001, 8002]
}

dynamic "ingress" {
  for_each = local.app_ports
  content {
    description     = "Allow port ${ingress.value} from ALB"
    from_port       = ingress.value
    to_port         = ingress.value
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }
}
```

### 2. ECS Task Role Added

Added `aws_iam_role.ecs_task_role` alongside the
existing `ecs_task_execution_role`. They serve
different purposes:

| Role                      | Purpose                                        | Used By   |
|---------------------------|------------------------------------------------|-----------|
| `ecs_task_execution_role` | Pull ECR image, write CloudWatch logs          | ECS agent |
| `ecs_task_role`           | Application AWS permissions (DynamoDB, S3 etc) | App code  |

The task role has a safe baseline policy allowing
CloudWatch log writes. Extend it per application
when AWS service access is needed:

```hcl
# Example — add DynamoDB access for school app
resource "aws_iam_role_policy" "school_dynamodb" {
  name = "school-dynamodb-policy"
  role = aws_iam_role.ecs_task_role.id

  policy = jsonencode({
    Statement = [{
      Effect   = "Allow"
      Action   = ["dynamodb:GetItem", "dynamodb:PutItem"]
      Resource = "arn:aws:dynamodb:us-east-1:*:table/school-*"
    }]
  })
}
```

---

## Port Assignment Convention

Each application gets a unique port. This prevents
confusion and makes the security group `app_ports`
list meaningful.

| Application    | Port | Status                      |
|----------------|------|-----------------------------|
| Dashboard      | 8000 | ✅ Deployed                 |
| Portfolio      | 8001 | ✅ Deployed                 |
| School         | 8002 | ✅ Ready — pending DB setup |
| Banking        | 8003 | 🔲 Future                   |
| Personal Bio   | 8004 | 🔲 Future                   |
| Small Business | 8005 | 🔲 Future                   |
| E-commerce     | 8006 | 🔲 Future                   |

When adding a new application:
```hcl
# Step 1 — Add port to shared infrastructure
# modules/security/main.tf
app_ports = [8000, 8001, 8002, 8003]  # add new port

# Step 2 — Apply shared infrastructure to update security group
cd resources/shared/dev && terraform apply
```

---

## Session Workflow After Refactoring

### Deploy

```bash
# Step 1 — Deploy shared once — leave running permanently
cd resources/shared/dev
terraform init
terraform apply -var-file="terraform.tfvars"
# 21 resources — VPC, security, IAM, EC2 — ALL FREE

# Step 2 — Deploy any app independently
cd resources/dashboard/dev
terraform init && terraform apply -var-file="terraform.tfvars"
echo "Dashboard: $(terraform output -raw alb_dns_name)"

cd resources/portfolio/dev
terraform init && terraform apply
echo "Portfolio: $(terraform output -raw portfolio_alb_dns_name)"

cd resources/school/dev
terraform init && terraform apply -var-file="terraform.tfvars"
echo "School: $(terraform output -raw school_alb_dns_name)"
```

### Destroy — Always in Reverse Order

```bash
# Apps first — any order between themselves
cd resources/school/dev    && terraform destroy
cd resources/portfolio/dev && terraform destroy
cd resources/dashboard/dev && terraform destroy

# Shared last — only after all apps are destroyed
cd resources/shared/dev    && terraform destroy
```

### Verify Clean Destroy

```bash
# Confirm no ALBs running
aws elbv2 describe-load-balancers \
  --query "LoadBalancers[*].{Name:LoadBalancerName,State:State.Code}" \
  --output table

# Confirm no ECS clusters running
aws ecs list-clusters --output table

# Confirm shared resources destroyed (if you destroyed shared)
aws ec2 describe-vpcs \
  --filters "Name=tag:Project,Values=mecandjeo-infra" \
  --query "Vpcs[*].VpcId" \
  --output table
```

---

## Pipeline Changes

### Dashboard Pipeline Updated

The dashboard pipeline working directory changed from
`resources/dev` to `resources/dashboard/dev`.

Variables `allowed_ssh_cidr` and `public_key` removed
from dashboard pipeline — these are now managed by
shared infrastructure and not needed by the dashboard.

```yaml
# Before
working-directory: resources/dev
-var="allowed_ssh_cidr=${{ vars.ALLOWED_SSH_CIDR_DEV }}"
-var="public_key=${{ vars.PUBLIC_KEY }}"

# After
working-directory: resources/dashboard/dev
# No SSH or compute variables needed
```

Path trigger updated:
```yaml
# Before
- 'resources/dev/**'

# After
- 'resources/dashboard/**'
```

### Portfolio Pipeline Updated

Portfolio `terraform_remote_state` updated to read
from shared state instead of dashboard state:

```hcl
# Before
data "terraform_remote_state" "dashboard" {
  key = "mecandjeo-dashboard/dev/terraform.tfstate"
}

# After
data "terraform_remote_state" "shared" {
  key = "mecandjeo-shared/dev/terraform.tfstate"
}
```

### Pending — Shared Infrastructure Pipeline

A dedicated pipeline for shared infrastructure is
needed so it can be deployed and updated via CI/CD.

File to create: `.github/workflows/shared-infra-cicd.yml`

This pipeline:
- Triggers on changes to `resources/shared/**` and `modules/**`
- Runs validate and plan only on pull requests
- Requires manual approval for apply
- Never runs destroy automatically

---

## School App Integration

The school platform was migrated from its own separate
repository (`github.com/s8mike/mecandjeo-school-platform`)
into this monorepo at `apps/mecandjeo-school/`.

### What Changed

| Item               | Before                                  | After                                    |
|--------------------|-----------------------------------------|------------------------------------------|
| App code location  | `school-platform/app/`                  | `apps/mecandjeo-school/app/`             |
| Terraform location | `school-platform/terraform/`            | `resources/school/dev/`                  |
| Modules            | Own copy in school repo                 | Shared modules in this repo              |
| State key          | `school-platform/dev/terraform.tfstate` | `mecandjeo-school/dev/terraform.tfstate` |
| Container port     | 8000                                    | 8002                                     |
| Pipeline           | None                                    | `school-cicd.yml` (pending)              |

### School App Current Status

The school app requires a PostgreSQL database via
`DATABASE_URL` environment variable. It crashes on
startup without it.

**Current approach:** Build and test locally with
PostgreSQL before deploying to AWS. When ready for
AWS deployment choose one of:

- SQLite for dev — no infrastructure, zero cost
- RDS PostgreSQL for prod — persistent, ~$15/month
- External PostgreSQL (Supabase/Neon) — free tier available

The school Terraform infrastructure (`resources/school/dev/`)
is fully configured and ready. Only the database
dependency needs resolving before first successful deployment.

---

## Adding a New Application — Standard Process

Follow this checklist for every new application:

```bash
# 1. Create ECR repository
aws ecr create-repository \
  --repository-name mecandjeo-infra-{appname} \
  --image-scanning-configuration scanOnPush=true \
  --region us-east-1

# 2. Add port to security group
# Edit modules/security/main.tf
# app_ports = [8000, 8001, 8002, NEW_PORT]

# 3. Apply shared to update security group
cd resources/shared/dev && terraform apply -var-file="terraform.tfvars"

# 4. Create app directories
mkdir -p apps/mecandjeo-{appname}
mkdir -p resources/{appname}/dev

# 5. Create Terraform files
# Copy resources/school/dev/ as template
# Update project_name, container_port, state key

# 6. Create pipeline file
# Copy .github/workflows/school-cicd.yml as template
# Update ECR_REPOSITORY, DOCKERHUB_REPO, cluster names

# 7. Build and push Docker image
docker build --file apps/mecandjeo-{appname}/Dockerfile \
  --tag mecandjeo-{appname}:v1.0.0 apps/mecandjeo-{appname}/

# 8. Deploy
cd resources/{appname}/dev
terraform init && terraform apply -var-file="terraform.tfvars"
```

---

## Problems Encountered During Refactoring

### Problem 1 — Module Path Depth
**Error:** `Unable to evaluate directory symlink`

**Cause:** New directories are three levels deep
(`resources/shared/dev/`) requiring `../../../modules/`
not `../../modules/`.

**Resolution:** Updated all module source paths in
new directories to use three levels up.

### Problem 2 — IAM Task Role Already Exists
**Error:** `EntityAlreadyExists: Role with name mecandjeo-infra-dev-ecs-task-role already exists`

**Cause:** Dashboard pipeline was still pointing to
old `resources/dev/` which included the security module.
Shared infrastructure had already created the IAM role.
Pipeline tried to create it again — conflict.

**Resolution:** Updated dashboard pipeline working
directory to `resources/dashboard/dev/`. Dashboard
no longer manages IAM — shared infrastructure owns it.

### Problem 3 — Pipeline Passing Obsolete Variables
**Error:** `Value for undeclared variable: public_key` and `allowed_ssh_cidr`

**Cause:** Dashboard pipeline was still passing
`public_key` and `allowed_ssh_cidr` as `-var` flags.
These variables no longer exist in `resources/dashboard/dev/variables.tf`
— they moved to shared infrastructure.

**Resolution:** Removed both variables from all
dashboard pipeline `terraform plan` and `terraform apply`
steps.

### Problem 4 — School App Database Dependency
**Error:** `sqlalchemy.exc.ArgumentError: Expected string or URL object, got None`

**Cause:** School app requires `DATABASE_URL` environment
variable for PostgreSQL connection. ECS task definition
does not pass this variable. App crashes on startup.

**Resolution:** Deferred — school app will be built
and tested locally with PostgreSQL first. AWS deployment
planned after database strategy is decided (SQLite for
dev, RDS for prod, or external service).

### Problem 5 — Terraform Registry Network Timeout
**Error:** `could not connect to registry.terraform.io: context deadline exceeded`

**Cause:** Temporary network connectivity issue
prevented provider download during `terraform init`.

**Resolution:** Copied `.terraform` directory from
an already-initialised directory (portfolio) to school:
```bash
cp -r resources/portfolio/dev/.terraform \
      resources/school/dev/.terraform
terraform init -reconfigure
```

---

## Key Concepts Learned

### Shared Infrastructure Pattern
Free AWS resources — VPC, security groups, IAM roles —
deploy once and stay running permanently. Chargeable
resources — ALB, ECS tasks — deploy per session and
destroy when done. This eliminates rebuild time and
removes inter-app dependencies.

### terraform_remote_state for Cross-State Sharing
Each application reads shared infrastructure values
from the shared state file via `terraform_remote_state`.
The consuming app has read-only access — it cannot
modify shared state. This enforces clear ownership
boundaries between infrastructure layers.

### Destroy Order Matters
Always destroy in reverse dependency order. Apps that
read from shared state must be destroyed before shared
infrastructure. Destroying shared first leaves app
state files with broken remote state references.

### Port Uniqueness Across Apps
Each application must have a unique container port.
The shared ECS security group allows all app ports
via a `dynamic` ingress block. New ports are added
to `app_ports` list in `modules/security/main.tf`
and shared infrastructure is reapplied.

### Monorepo Integration
Migrating the school app from its own repository
into the monorepo standardises the pattern — one
set of modules, one pipeline structure, one place
to look. The original repository is archived for
reference but all active development moves here.

### Pipeline Working Directory
Each application pipeline must point to its own
`resources/{app}/dev/` working directory. Using the
wrong working directory causes the wrong Terraform
configuration to apply — potentially creating
duplicate resources or failing with conflict errors.

---

## Pending Items

| Item                                 | File                                      | Priority |
|--------------------------------------|-------------------------------------------|----------|
| Shared infrastructure pipeline       | `.github/workflows/shared-infra-cicd.yml` | High     |
| School pipeline                      | `.github/workflows/school-cicd.yml`       | Medium   |
| School database setup                | `apps/mecandjeo-school/app/database.py`   | Medium   |
| Update README.md                     | `README.md`                               | Low      |
| Update POST-DEPLOYMENT-ACTIVITIES.md | `POST-DEPLOYMENT-ACTIVITIES.md`           | Low      |

---

## Verification Checklist

After every refactoring apply confirm:

```bash
# All state keys exist
aws s3 ls s3://mecandjeo-infra-dev-tfstate/ --recursive

# Shared outputs available
cd resources/shared/dev && terraform output

# Each app reads shared state correctly
cd resources/dashboard/dev && terraform output
cd resources/portfolio/dev && terraform output
cd resources/school/dev    && terraform output

# All apps accessible in browser
curl http://$(cd resources/dashboard/dev && \
  terraform output -raw alb_dns_name)/health
curl http://$(cd resources/portfolio/dev && \
  terraform output -raw portfolio_alb_dns_name)/health
```

---

*MecanjeoOps Infrastructure — Refactoring Documentation*
*Mecandjeo Technology — Platform Engineering — 2026*
```

---

Commit this file:

```bash
git add REFACTORING-SHARED-INFRASTRUCTURE.md
git commit -m "Add: REFACTORING-SHARED-INFRASTRUCTURE.md — complete refactoring documentation"
git push
```

---

### Still Pending

```
.github/workflows/shared-infra-cicd.yml  ← shared infrastructure pipeline
.github/workflows/school-cicd.yml        ← school app pipeline (after DB sorted)
```

Shall we write the shared infrastructure pipeline next? 🚀