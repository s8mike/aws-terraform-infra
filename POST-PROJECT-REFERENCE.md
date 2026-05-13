# Claude 2/5/26
---

**File title: `POST-PROJECT-REFERENCE.md`**

---

```markdown
# Post-Project Reference Guide
## mecandjeo-infra — Questions and Answers After Project Completion
**Mecandjeo Technology — Platform Engineering**

---

## 1. Can You Experiment by Making Changes and See Them Deployed?

### Short Answer
Yes — absolutely. This is exactly what the pipeline was built for.

### What to Do
Make any change to the application code, commit, and push to main:

```bash
git add .
git commit -m "your change description"
git push origin main
```

The pipeline triggers automatically:
- Validates Terraform code
- Builds a new Docker image with a new commit SHA tag
- Pushes to Docker Hub and ECR
- Deploys to AWS ECS via rolling update
- New containers replace old ones with zero downtime
- Open the ALB DNS name in browser to see changes live

### What Level of Changes Can You Make to the App?

**Safe — no infrastructure changes needed:**
- Any change to `apps/mecandjeo-dashboard/static/index.html` — UI text, layout, colours
- Any change to `apps/mecandjeo-dashboard/static/style.css` — styling, themes
- Any change to `apps/mecandjeo-dashboard/static/app.js` — frontend logic, refresh interval
- Any change to `apps/mecandjeo-dashboard/main.py` — API endpoints, data, business logic
- Adding new API endpoints to FastAPI
- Updating the deployment history data
- Changing the application version number

**Requires small Terraform changes:**
- Adding a new environment variable → update `modules/ecs/main.tf` environment block
- Changing the container port → update `terraform.tfvars` and security group
- Adding a second container → update task definition

**Requires significant Terraform changes:**
- Adding a database → new RDS or DynamoDB module
- Adding a second application → new ECS service, ALB, target group
- Adding HTTPS → new ALB listener and ACM certificate

### Try This First — Simple UI Change
Open `apps/mecandjeo-dashboard/static/index.html` and change the footer text.
Push and watch the pipeline deploy it automatically.
That single experience proves the entire CI/CD loop works end to end.

---

## 2. Can You Use the Same Infrastructure for Another Application?

### Short Answer
Yes — but each application needs its own ECS service, ALB, and target group.
They share the VPC, subnets, security groups, ECS cluster, and IAM roles.

### What Is Shared (provisioned once)
```
VPC and subnets          ← one per environment, shared by all apps
Security groups          ← shared base rules, app-specific rules added
ECS cluster              ← one cluster hosts all application services
IAM roles                ← shared task execution role
S3 state bucket          ← one per environment
```

### What Each Application Gets Independently
```
ECS service              ← separate service per app
ECS task definition      ← separate task definition per app
ALB                      ← separate load balancer per app (or path-based routing)
Target group             ← separate target group per app
CloudWatch log group     ← separate logs per app
ECR repository           ← separate image registry per app
Container image          ← separate Docker image per app
Auto scaling policies    ← separate scaling per app
```

### How It Works in `resources/dev/main.tf`
```hcl
# App 1 — Dashboard (already exists)
module "ecs_dashboard" {
  source          = "../../modules/ecs"
  project_name    = "mecandjeo-dashboard"
  container_image = var.dashboard_image
  container_port  = 8000
  target_group_arn = module.alb_dashboard.target_group_arn
}

# App 2 — New Application
module "ecs_banking_app" {
  source          = "../../modules/ecs"
  project_name    = "mecandjeo-banking"
  container_image = var.banking_image
  container_port  = 3000
  target_group_arn = module.alb_banking.target_group_arn
}
```

### Limitations
- Each additional ALB costs ~$0.008/hr — budget accordingly
- ECS Fargate free tier is limited — running multiple apps uses it faster
- The same VPC CIDR supports many apps — no IP limitation concern
- IAM roles can be shared but apply least privilege per app in production

### What Must Change for Each New Application
| Item                    | Change Required                    |
|-------------------------|------------------------------------|
| `project_name` variable | Unique name per app                |
| `container_port`        | Match the app's listening port     |
| `container_image`       | Point to the app's ECR repository  |
| `health_check_path`     | Match the app's health endpoint    |
| ECR repository          | Create a new one manually per app  |
| Pipeline file           | Create a new workflow file per app |
| GitHub Variables        | Add image variable per app         |

---

## 3. Same Repo or Different Repos for Multiple Applications?

### The Two Patterns

**Pattern A — Monorepo (all apps in one repo)**
```
aws-terraform-infra/
├── modules/              ← shared infrastructure
├── resources/dev/        ← calls all app modules
├── apps/
│   ├── mecandjeo-dashboard/
│   ├── mecandjeo-banking/
│   └── mecandjeo-school/
└── .github/workflows/
    ├── dashboard-cicd.yml
    ├── banking-cicd.yml
    └── school-cicd.yml
```

**Pattern B — Polyrepo (each app in its own repo)**
```
aws-terraform-infra/     ← infrastructure only
mecandjeo-dashboard/     ← dashboard app only
mecandjeo-banking/       ← banking app only
mecandjeo-school/        ← school app only
```

### When to Use Each

| Situation                                      | Recommended Pattern                                  |
|------------------------------------------------|------------------------------------------------------|
| Learning, solo developer, closely related apps | Monorepo — simpler, everything visible               |
| Team with separate ownership per app           | Polyrepo — clean boundaries, independent deployments |
| Apps share the same infrastructure             | Monorepo — easier to coordinate                      |
| Apps are independent products                  | Polyrepo — no accidental cross-impacts               |
| You want one place to see everything           | Monorepo                                             |
| You want independent deployment velocity       | Polyrepo                                             |

### Recommendation for This Project
**Stay monorepo while learning.** Add new apps under `apps/` with their own
pipeline files under `.github/workflows/`. When you have two or more apps
running simultaneously and teams start stepping on each other — that is
the signal to split into polyrepo.

---

## 4. Should You Manually Delete ECR After Project Completion?

### Short Answer
Only if you are completely done with the project and want a clean AWS account.
If you plan to continue developing or add more applications — keep it.

### ECR Free Tier
- **500MB free per month** — your image is approximately 180MB
- Storing the image costs **nothing** as long as you stay under 500MB
- No risk of unexpected charges from keeping it

### When to Delete ECR
- You are completely done with the project
- You want to clean up your AWS account entirely
- You are hitting the 500MB free tier limit (unlikely for one image)

### CLI Commands to Delete ECR

**Delete all images from the repository first:**
```bash
# Individual commands — understand each step

# Step 1 — List all image digests in the repository
aws ecr list-images \
  --repository-name mecandjeo-infra-dev \
  --query "imageIds[*]" \
  --output json

# Step 2 — Delete all images
aws ecr batch-delete-image \
  --repository-name mecandjeo-infra-dev \
  --image-ids "$(aws ecr list-images \
    --repository-name mecandjeo-infra-dev \
    --query 'imageIds[*]' \
    --output json)"

# Step 3 — Delete the empty repository
aws ecr delete-repository \
  --repository-name mecandjeo-infra-dev \
  --region us-east-1
```

**Optional bundled version — deletes images and repository in one block:**
```bash
# Delete all images then delete repository
aws ecr batch-delete-image \
  --repository-name mecandjeo-infra-dev \
  --image-ids "$(aws ecr list-images \
    --repository-name mecandjeo-infra-dev \
    --query 'imageIds[*]' \
    --output json)" && \
aws ecr delete-repository \
  --repository-name mecandjeo-infra-dev \
  --region us-east-1 && \
echo "ECR repository deleted successfully"
```

**Verify deletion:**
```bash
aws ecr describe-repositories \
  --repository-names mecandjeo-infra-dev \
  --region us-east-1 2>/dev/null \
  || echo "Repository confirmed deleted"
```

### Delete S3 State Bucket (Only When Completely Done)

```bash
# Empty the bucket first
aws s3 rm s3://mecandjeo-infra-dev-tfstate --recursive

# Delete the bucket
aws s3api delete-bucket \
  --bucket mecandjeo-infra-dev-tfstate \
  --region us-east-1

echo "S3 state bucket deleted"
```

## 5. Managing Multiple Applications in One main.tf

Excellent questions — these go to the heart of how real platform teams manage multiple applications. Let me answer both clearly.

---

## Question 1 — How Do You Differentiate Which App to Deploy?

### The Short Answer
You do not choose which app to deploy at the Terraform level — **Terraform always deploys everything declared in `main.tf`**. The differentiation happens at the **pipeline level** — each app has its own pipeline file that only updates its own image variable.

### How It Works in Practice

```
resources/dev/main.tf declares ALL apps:
  module "ecs_dashboard" { container_image = var.dashboard_image }
  module "ecs_banking"   { container_image = var.banking_image }
  module "ecs_school"    { container_image = var.school_image }

Pipeline for dashboard runs:
  terraform apply -var="dashboard_image=NEW_IMAGE"
  # banking_image and school_image read from state — unchanged
  # Only dashboard ECS service updates

Pipeline for banking runs:
  terraform apply -var="banking_image=NEW_IMAGE"
  # dashboard_image and school_image read from state — unchanged
  # Only banking ECS service updates
```

The key insight is that **Terraform only changes what differs from state**. If `banking_image` is not passed in the dashboard pipeline apply, Terraform reads the current value from S3 state and leaves it exactly as it is.

---

## Question 2 — How Do You Handle Different tfvars Per App?

### The Short Answer
Each app does not need its own `tfvars` file. Instead you have **one `tfvars` file with all app variables** — each app has its own named variable.

### How the Single tfvars Looks With Multiple Apps

```hcl
# resources/dev/terraform.tfvars.pipeline

# ── Shared infrastructure ─────────────────────────
aws_region   = "us-east-1"
project_name = "mecandjeo-infra"
environment  = "dev"
vpc_cidr     = "10.0.0.0/16"

# ── App 1 — Dashboard ─────────────────────────────
dashboard_image = "776735193826.dkr.ecr.us-east-1.amazonaws.com/mecandjeo-dashboard:latest"
dashboard_port  = 8000

# ── App 2 — Banking App ───────────────────────────
banking_image = "776735193826.dkr.ecr.us-east-1.amazonaws.com/mecandjeo-banking:latest"
banking_port  = 3000

# ── App 3 — School App ────────────────────────────
school_image = "776735193826.dkr.ecr.us-east-1.amazonaws.com/mecandjeo-school:latest"
school_port  = 5000
```

### How Each Pipeline Overrides Only Its Own Image

```yaml
# .github/workflows/dashboard-cicd.yml
- name: Terraform Apply
  run: |
    terraform apply \
      -var-file="terraform.tfvars.pipeline" \
      -var="dashboard_image=${{ needs.docker.outputs.image_uri }}" \
      # banking_image and school_image come from tfvars — unchanged
```

```yaml
# .github/workflows/banking-cicd.yml
- name: Terraform Apply
  run: |
    terraform apply \
      -var-file="terraform.tfvars.pipeline" \
      -var="banking_image=${{ needs.docker.outputs.image_uri }}" \
      # dashboard_image and school_image come from tfvars — unchanged
```

---

## The Complete Picture — How All Three Work Together

```
┌─────────────────────────────────────────────────────────┐
│           resources/dev/terraform.tfvars.pipeline       │
│                                                         │
│  dashboard_image = "...mecandjeo-dashboard:abc12345"    │
│  banking_image   = "...mecandjeo-banking:def67890"      │
│  school_image    = "...mecandjeo-school:ghi11121"       │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│              resources/dev/main.tf                      │
│                                                         │
│  module "ecs_dashboard" {                               │
│    container_image = var.dashboard_image                │
│  }                                                      │
│  module "ecs_banking" {                                 │
│    container_image = var.banking_image                  │
│  }                                                      │
│  module "ecs_school" {                                  │
│    container_image = var.school_image                   │
│  }                                                      │
└─────────────────────────────────────────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          ▼               ▼               ▼
   dashboard          banking           school
   pipeline           pipeline          pipeline
   updates            updates           updates
   dashboard_image    banking_image     school_image
   only               only              only
```

---

## What Happens in the S3 State File

When the dashboard pipeline runs and only passes `dashboard_image`:

```
State before:
  dashboard_image = "mecandjeo-dashboard:abc12345"
  banking_image   = "mecandjeo-banking:def67890"
  school_image    = "mecandjeo-school:ghi11121"

Dashboard pipeline applies with new image:
  dashboard_image = "mecandjeo-dashboard:NEW_TAG"  ← changes
  banking_image   = read from state = "def67890"   ← unchanged
  school_image    = read from state = "ghi11121"   ← unchanged

State after:
  dashboard_image = "mecandjeo-dashboard:NEW_TAG"  ← updated
  banking_image   = "mecandjeo-banking:def67890"   ← preserved
  school_image    = "mecandjeo-school:ghi11121"    ← preserved
```

This is Terraform's idempotency in action — it only changes what is explicitly different.

---

## Summary Table

| Question                              | Answer                                                          |
|---------------------------------------|-----------------------------------------------------------------|
| How to deploy only one app?           | Each app has its own pipeline — only its image variable changes |
| How does Terraform know what changed? | It compares current state with new configuration — only diffs are applied |
| One tfvars or many?                   | One tfvars with named variables per app — simpler, no duplication |
| What if an app has unique config?     | Add app-specific variables with clear naming — `banking_port`, `school_cpu` etc |
| What stays the same across all apps?  | VPC, subnets, security groups, cluster, IAM — provisioned once, shared |
| What is unique per app?               | ECS service, ALB, target group, ECR repo, CloudWatch log group, image variable |

---

### Recommendation
**Keep both ECR and S3 for now.** You are planning to build more applications
on this infrastructure. The storage costs are zero within free tier limits.
Delete them only when you are permanently shutting down the project.

---

## What Comes Next
The infrastructure is complete and proven. The next applications to build
and deploy using this same infrastructure:

| Application              | Stack Suggestion          | Complexity                 |
|--------------------------|---------------------------|----------------------------|
| Personal portfolio / bio | FastAPI + HTML            | Low — similar to dashboard |
| Small business website   | FastAPI + HTML/CSS        | Low                        |
| School management app    | FastAPI + SQLite/DynamoDB | Medium                     |
| Banking demo app         | FastAPI + DynamoDB + auth | Medium-High                |
| E-commerce store         | FastAPI + RDS + S3        | High                       |

Each application follows the same four phases:
1. Build the application locally
2. Containerise with Docker and push to ECR and Docker Hub
3. Deploy using existing Terraform infrastructure
4. Wire the CI/CD pipeline

The infrastructure never needs to be rebuilt from scratch.
Only the application code, Docker image, and pipeline file change.

---

*mecandjeo-infra — Post-Project Reference*
*Mecandjeo Technology — Platform Engineering — 2026*
```

---

That is your reference document. Save it as `POST-PROJECT-REFERENCE.md` anywhere convenient — project root, a notes folder, or alongside the other READMEs.

---

**On your note about building more applications** — confirmed. When you are ready say the word and we pick up with the next application. My suggestion for starting application would be a **Personal Portfolio / Bio Data app** — it is simple enough to build quickly, visually impressive to demo, and directly relevant to your job search since it showcases you personally. But the choice is yours. 🚀