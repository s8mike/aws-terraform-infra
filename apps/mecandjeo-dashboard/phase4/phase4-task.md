## Phase 4 — Wire the CI/CD Pipeline

---

### What We Are Doing in This Phase

We are updating the GitHub Actions pipeline from Phase 2 of the infrastructure project to build and deploy the real MecanjeoOps Dashboard instead of the nginx placeholder. Every push to main will automatically build the Docker image, push to both Docker Hub and ECR, and deploy to AWS without any manual steps.

```
Developer pushes code to main
        │
        ▼
GitHub Actions triggered automatically
        │
        ├── Job 1: validate
        │     terraform fmt, validate, plan
        │
        ├── Job 2: docker
        │     build real Dockerfile
        │     push to Docker Hub (s8mike)
        │     push to AWS ECR
        │
        ├── Job 3: deploy-dev
        │     terraform apply
        │     ECS pulls new image automatically
        │
        └── Job 4: deploy-prod (manual approval)
              terraform apply to prod
```

---

### What Changes from the Original Pipeline

| Item | Before | After |
|---|---|---|
| Docker image source | `docker pull nginx:latest` | `docker build` from real Dockerfile |
| Dockerfile location | None | `apps/mecandjeo-dashboard/Dockerfile` |
| Docker Hub push | Not included | Added — pushes to `s8mike/mecandjeo-dashboard` |
| Container port | `80` | `8000` |
| Health check path | `/` | `/health` |
| ECR management | ECR created by Terraform | ECR created manually — pipeline only pushes |
| Backend bucket | Created by Terraform | Created manually — pipeline uses existing |

---

### Pre-Flight Checks

Before touching any pipeline code confirm these are ready:

```bash
# 1. Confirm Docker Hub credentials work
docker login --username s8mike

# 2. Confirm ECR repository exists
aws ecr describe-repositories \
  --repository-names mecandjeo-infra-dev \
  --query "repositories[0].repositoryName" \
  --output text

# 3. Confirm image exists in ECR
aws ecr describe-images \
  --repository-name mecandjeo-infra-dev \
  --query "imageDetails[*].imageTags" \
  --output table

# 4. Confirm S3 backend bucket exists
aws s3api head-bucket \
  --bucket mecandjeo-infra-dev-tfstate \
  && echo "Bucket exists" \
  || echo "Create bucket first"

# 5. Confirm GitHub secrets are set
# Go to: github.com/s8mike/aws-terraform-infra
# Settings → Secrets and variables → Actions
# Confirm all secrets listed in Section 2 exist
```

---

### Step 1: Add Docker Hub Secret to GitHub

We need one new secret that was not in the original pipeline.

Go to **GitHub → Settings → Secrets and variables → Actions → New repository secret:**

| Secret Name | Value |
|---|---|
| `DOCKERHUB_USERNAME` | `s8mike` |
| `DOCKERHUB_TOKEN` | Your Docker Hub access token |

All existing secrets from the infrastructure pipeline should already be there:

| Secret | Value |
|---|---|
| `AWS_ACCESS_KEY_ID` | Your IAM access key |
| `AWS_SECRET_ACCESS_KEY` | Your IAM secret key |
| `AWS_ACCOUNT_ID` | `776735193826` |
| `AWS_REGION` | `us-east-1` |
| `TF_STATE_BUCKET_DEV` | `mecandjeo-infra-dev-tfstate` |
| `TF_DYNAMODB_TABLE_DEV` | Not needed anymore — using `use_lockfile` |
| `ALLOWED_SSH_CIDR_DEV` | `YOUR_IP/32` |

---

### Step 2: Set Up GitHub Production Environment

If not already done from the infrastructure project:

1. Go to **github.com/s8mike/aws-terraform-infra**
2. Click **Settings → Environments → New environment**
3. Name it exactly: `production`
4. Click **Required reviewers**
5. Add your GitHub username
6. Click **Save protection rules**

---

### Step 3: Update the Pipeline File

Replace the entire contents of `.github/workflows/terraform-cicd.yml` with:

```yaml
# ─────────────────────────────────────────────────────────────
# GitHub Actions CI/CD Pipeline
# Project:     mecandjeo-infra
# Application: MecanjeoOps Dashboard
# Description: Builds real Docker image from Dockerfile,
#              pushes to Docker Hub and ECR,
#              deploys to dev automatically,
#              deploys to prod with manual approval.
#
# Required GitHub Secrets:
#   AWS_ACCESS_KEY_ID       — IAM user access key
#   AWS_SECRET_ACCESS_KEY   — IAM user secret key
#   AWS_ACCOUNT_ID          — 776735193826
#   AWS_REGION              — us-east-1
#   TF_STATE_BUCKET_DEV     — mecandjeo-infra-dev-tfstate
#   TF_STATE_BUCKET_PROD    — mecandjeo-infra-prod-tfstate
#   ALLOWED_SSH_CIDR_DEV    — your IP/32
#   ALLOWED_SSH_CIDR_PROD   — your IP/32
#   DOCKERHUB_USERNAME      — s8mike
#   DOCKERHUB_TOKEN         — Docker Hub access token
#
# Required GitHub Environment:
#   production              — with required reviewers set
# ─────────────────────────────────────────────────────────────

name: MecanjeoOps Dashboard CI/CD

on:
  push:
    branches:
      - main
    paths:
      - 'apps/mecandjeo-dashboard/**'
      - 'modules/**'
      - 'resources/dev/**'
      - '.github/workflows/terraform-cicd.yml'
  pull_request:
    branches:
      - main

# Prevent concurrent runs on same branch
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

env:
  TF_VERSION:       "1.5.0"
  AWS_REGION:       ${{ secrets.AWS_REGION }}
  ECR_REGISTRY:     ${{ secrets.AWS_ACCOUNT_ID }}.dkr.ecr.${{ secrets.AWS_REGION }}.amazonaws.com
  ECR_REPOSITORY:   "mecandjeo-infra-dev"
  DOCKERHUB_REPO:   "${{ secrets.DOCKERHUB_USERNAME }}/mecandjeo-dashboard"
  APP_VERSION:      "1.0.0"
  IMAGE_TAG:        ${{ github.sha }}

# ─────────────────────────────────────────────────────────────
# JOB 1 — VALIDATE
# Runs on every push and pull request
# Checks formatting, validates syntax, runs terraform plan
# No AWS resources are created
# ─────────────────────────────────────────────────────────────
jobs:
  validate:
    name: Terraform Validate
    runs-on: ubuntu-latest

    steps:
      # Step 1 — Check out the repository code
      - name: Checkout code
        uses: actions/checkout@v4

      # Step 2 — Install the specified Terraform version
      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: ${{ env.TF_VERSION }}

      # Step 3 — Configure AWS credentials for plan
      # Uses GitHub secrets — never hardcode credentials
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id:     ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region:            ${{ env.AWS_REGION }}

      # Step 4 — Check Terraform formatting
      # terraform fmt -check exits with error if any file is not formatted
      # This enforces consistent code style across the team
      - name: Terraform Format Check
        run: terraform fmt -check -recursive

      # Step 5 — Initialize Terraform with dev backend
      # Downloads provider plugins and configures S3 backend
      - name: Terraform Init
        run: |
          terraform init \
            -backend-config="bucket=${{ secrets.TF_STATE_BUCKET_DEV }}" \
            -backend-config="key=dev/terraform.tfstate" \
            -backend-config="region=${{ env.AWS_REGION }}" \
            -backend-config="use_lockfile=true" \
            -backend-config="encrypt=true"
        working-directory: resources/dev

      # Step 6 — Validate Terraform configuration syntax
      # Checks that all resource references and variable types are correct
      - name: Terraform Validate
        run: terraform validate
        working-directory: resources/dev

      # Step 7 — Run Terraform plan and save output
      # This shows exactly what would change without applying anything
      # The plan is saved as an artifact for review on pull requests
      - name: Terraform Plan
        run: |
          terraform plan \
            -var="aws_region=${{ env.AWS_REGION }}" \
            -var="project_name=mecandjeo-infra" \
            -var="environment=dev" \
            -var="allowed_ssh_cidr=${{ secrets.ALLOWED_SSH_CIDR_DEV }}" \
            -var="vpc_cidr=10.0.0.0/16" \
            -var='public_subnet_cidrs=["10.0.1.0/24","10.0.2.0/24"]' \
            -var='private_subnet_cidrs=["10.0.3.0/24","10.0.4.0/24"]' \
            -var='availability_zones=["us-east-1a","us-east-1b"]' \
            -var="instance_type=t3.micro" \
            -var="container_image=${{ env.ECR_REGISTRY }}/${{ env.ECR_REPOSITORY }}:${{ env.APP_VERSION }}" \
            -var="container_port=8000" \
            -var="task_cpu=256" \
            -var="task_memory=512" \
            -var="desired_count=2" \
            -var="health_check_path=/health" \
            -var="min_capacity=2" \
            -var="max_capacity=6" \
            -var="scale_out_cpu_threshold=70" \
            -var="scale_in_cpu_threshold=30" \
            -out=tfplan-dev \
            -no-color 2>&1 | tee plan-output-dev.txt
        working-directory: resources/dev

      # Step 8 — Upload plan output as artifact
      # This allows engineers to review the plan on pull requests
      # before any merge or deployment happens
      - name: Upload Plan Output
        uses: actions/upload-artifact@v4
        with:
          name:           terraform-plan-dev
          path:           resources/dev/plan-output-dev.txt
          retention-days: 5

      # Step 9 — Post plan summary to PR as a comment
      # Only runs on pull requests — not on direct pushes
      - name: Post Plan to PR
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const plan = fs.readFileSync(
              'resources/dev/plan-output-dev.txt', 'utf8'
            );
            const maxLength = 65000;
            const truncated = plan.length > maxLength
              ? plan.substring(0, maxLength) + '\n\n... truncated ...'
              : plan;
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner:        context.repo.owner,
              repo:         context.repo.repo,
              body: `## Terraform Plan — Dev\n\`\`\`\n${truncated}\n\`\`\``
            });

# ─────────────────────────────────────────────────────────────
# JOB 2 — DOCKER
# Builds real Docker image from apps/mecandjeo-dashboard/
# Pushes to Docker Hub and AWS ECR
# Runs only on push to main after validate passes
# ─────────────────────────────────────────────────────────────
  docker:
    name: Build and Push Docker Image
    runs-on: ubuntu-latest
    needs: validate
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'

    outputs:
      image_uri: ${{ steps.build.outputs.image_uri }}
      image_tag: ${{ steps.build.outputs.image_tag }}

    steps:
      # Step 1 — Check out repository
      - name: Checkout code
        uses: actions/checkout@v4

      # Step 2 — Configure AWS credentials for ECR access
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id:     ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region:            ${{ env.AWS_REGION }}

      - name: Login to Docker Hub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}

      - name: Login to Amazon ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v2

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Build Docker image
        id: build
        env:
          SHORT_SHA: ${{ github.sha }}
        run: |
          # Use short SHA for cleaner image tags
          SHORT_TAG="${SHORT_SHA:0:8}"
          FULL_ECR_URI="${{ env.ECR_REGISTRY }}/${{ env.ECR_REPOSITORY }}"

          echo "Building MecanjeoOps Dashboard..."
          echo "Commit SHA : ${{ github.sha }}"
          echo "Short tag  : ${SHORT_TAG}"
          echo "ECR URI    : ${FULL_ECR_URI}"
          echo "Docker Hub : ${{ env.DOCKERHUB_REPO }}"

          # Build the image from the app Dockerfile
          docker build \
            --file apps/mecandjeo-dashboard/Dockerfile \
            --tag mecandjeo-dashboard:${SHORT_TAG} \
            --tag mecandjeo-dashboard:latest \
            --build-arg APP_VERSION=${{ env.APP_VERSION }} \
            apps/mecandjeo-dashboard/

          # Tag for Docker Hub
          docker tag mecandjeo-dashboard:${SHORT_TAG} \
            ${{ env.DOCKERHUB_REPO }}:${SHORT_TAG}
          docker tag mecandjeo-dashboard:${SHORT_TAG} \
            ${{ env.DOCKERHUB_REPO }}:latest

          # Tag for ECR
          docker tag mecandjeo-dashboard:${SHORT_TAG} \
            ${FULL_ECR_URI}:${SHORT_TAG}
          docker tag mecandjeo-dashboard:${SHORT_TAG} \
            ${FULL_ECR_URI}:latest

          # Push to Docker Hub
          echo "Pushing to Docker Hub..."
          docker push ${{ env.DOCKERHUB_REPO }}:${SHORT_TAG}
          docker push ${{ env.DOCKERHUB_REPO }}:latest

          # Push to ECR
          echo "Pushing to ECR..."
          docker push ${FULL_ECR_URI}:${SHORT_TAG}
          docker push ${FULL_ECR_URI}:latest

          # Set outputs for downstream jobs
          echo "image_uri=${FULL_ECR_URI}:${SHORT_TAG}" >> $GITHUB_OUTPUT
          echo "image_tag=${SHORT_TAG}" >> $GITHUB_OUTPUT

          echo "Build and push complete"
          echo "Docker Hub : ${{ env.DOCKERHUB_REPO }}:${SHORT_TAG}"
          echo "ECR        : ${FULL_ECR_URI}:${SHORT_TAG}"

# ─────────────────────────────────────────────────────────────
# JOB 3 — DEPLOY DEV
# Runs terraform apply against resources/dev automatically
# No manual approval required
# ECS automatically pulls the new image and does rolling update
# ─────────────────────────────────────────────────────────────
  deploy-dev:
    name: Deploy to Dev
    runs-on: ubuntu-latest
    needs: [validate, docker]
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'

    environment:
      name: development
      url:  http://${{ steps.apply.outputs.alb_dns_name }}

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: ${{ env.TF_VERSION }}
          terraform_wrapper: false

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id:     ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region:            ${{ env.AWS_REGION }}

      - name: Terraform Init
        run: |
          terraform init \
            -backend-config="bucket=${{ secrets.TF_STATE_BUCKET_DEV }}" \
            -backend-config="key=dev/terraform.tfstate" \
            -backend-config="region=${{ env.AWS_REGION }}" \
            -backend-config="use_lockfile=true" \
            -backend-config="encrypt=true"
        working-directory: resources/dev

      - name: Terraform Apply
        id: apply
        run: |
          terraform apply \
            -auto-approve \
            -var="aws_region=${{ env.AWS_REGION }}" \
            -var="project_name=mecandjeo-infra" \
            -var="environment=dev" \
            -var="allowed_ssh_cidr=${{ secrets.ALLOWED_SSH_CIDR_DEV }}" \
            -var="vpc_cidr=10.0.0.0/16" \
            -var='public_subnet_cidrs=["10.0.1.0/24","10.0.2.0/24"]' \
            -var='private_subnet_cidrs=["10.0.3.0/24","10.0.4.0/24"]' \
            -var='availability_zones=["us-east-1a","us-east-1b"]' \
            -var="instance_type=t3.micro" \
            -var="container_image=${{ needs.docker.outputs.image_uri }}" \
            -var="container_port=8000" \
            -var="task_cpu=256" \
            -var="task_memory=512" \
            -var="desired_count=2" \
            -var="health_check_path=/health" \
            -var="min_capacity=2" \
            -var="max_capacity=6" \
            -var="scale_out_cpu_threshold=70" \
            -var="scale_in_cpu_threshold=30" \
            -no-color

          # Capture ALB DNS for environment URL
          echo "alb_dns_name=$(terraform output -raw alb_dns_name)" \
            >> $GITHUB_OUTPUT
        working-directory: resources/dev

      - name: Wait for ECS Tasks to be Healthy
        run: |
          echo "Waiting for ECS tasks to reach RUNNING state..."
          MAX_ATTEMPTS=20
          ATTEMPT=0

          while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
            RUNNING=$(aws ecs describe-services \
              --cluster mecandjeo-infra-dev-cluster \
              --services mecandjeo-infra-dev-service \
              --query "services[0].runningCount" \
              --output text)

            DESIRED=$(aws ecs describe-services \
              --cluster mecandjeo-infra-dev-cluster \
              --services mecandjeo-infra-dev-service \
              --query "services[0].desiredCount" \
              --output text)

            echo "  Attempt ${ATTEMPT}/${MAX_ATTEMPTS} — Running: ${RUNNING}/${DESIRED}"

            if [ "${RUNNING}" = "${DESIRED}" ]; then
              echo "  All tasks running ✅"
              break
            fi

            ATTEMPT=$((ATTEMPT + 1))
            sleep 15
          done

          if [ $ATTEMPT -eq $MAX_ATTEMPTS ]; then
            echo "  Timed out waiting for tasks ❌"
            exit 1
          fi

      - name: Verify Application Health
        run: |
          ALB_DNS="${{ steps.apply.outputs.alb_dns_name }}"
          echo "Testing application health at: http://${ALB_DNS}/health"

          # Retry health check up to 10 times
          for i in $(seq 1 10); do
            STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
              http://${ALB_DNS}/health || echo "000")
            echo "  Attempt ${i}: HTTP ${STATUS}"
            if [ "${STATUS}" = "200" ]; then
              echo "  Application healthy ✅"
              break
            fi
            sleep 10
          done

          if [ "${STATUS}" != "200" ]; then
            echo "  Health check failed ❌"
            exit 1
          fi

      - name: Deployment Summary
        run: |
          echo "══════════════════════════════════════════"
          echo "  DEV DEPLOYMENT COMPLETE"
          echo "══════════════════════════════════════════"
          echo "  Environment : dev"
          echo "  Image       : ${{ needs.docker.outputs.image_uri }}"
          echo "  Tag         : ${{ needs.docker.outputs.image_tag }}"
          echo "  Commit      : ${{ github.sha }}"
          echo "  Branch      : ${{ github.ref_name }}"
          echo "  Dashboard   : http://${{ steps.apply.outputs.alb_dns_name }}"
          echo "══════════════════════════════════════════"

# ─────────────────────────────────────────────────────────────
# JOB 4 — DEPLOY PROD
# Pauses for manual approval via GitHub Environment protection
# Runs terraform apply against resources/prod after approval
# ─────────────────────────────────────────────────────────────
  deploy-prod:
    name: Deploy to Production
    runs-on: ubuntu-latest
    needs: [docker, deploy-dev]
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'

    environment:
      name: production
      url:  http://${{ steps.apply.outputs.alb_dns_name }}

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: ${{ env.TF_VERSION }}
          terraform_wrapper: false

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id:     ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region:            ${{ env.AWS_REGION }}

      - name: Terraform Init
        run: |
          terraform init \
            -backend-config="bucket=${{ secrets.TF_STATE_BUCKET_PROD }}" \
            -backend-config="key=prod/terraform.tfstate" \
            -backend-config="region=${{ env.AWS_REGION }}" \
            -backend-config="use_lockfile=true" \
            -backend-config="encrypt=true"
        working-directory: resources/prod

      - name: Terraform Plan
        run: |
          terraform plan \
            -var="aws_region=${{ env.AWS_REGION }}" \
            -var="project_name=mecandjeo-infra" \
            -var="environment=prod" \
            -var="allowed_ssh_cidr=${{ secrets.ALLOWED_SSH_CIDR_PROD }}" \
            -var="vpc_cidr=10.0.0.0/16" \
            -var='public_subnet_cidrs=["10.0.1.0/24","10.0.2.0/24"]' \
            -var='private_subnet_cidrs=["10.0.3.0/24","10.0.4.0/24"]' \
            -var='availability_zones=["us-east-1a","us-east-1b"]' \
            -var="instance_type=t3.micro" \
            -var="container_image=${{ needs.docker.outputs.image_uri }}" \
            -var="container_port=8000" \
            -var="task_cpu=512" \
            -var="task_memory=1024" \
            -var="desired_count=2" \
            -var="health_check_path=/health" \
            -var="min_capacity=2" \
            -var="max_capacity=10" \
            -var="scale_out_cpu_threshold=70" \
            -var="scale_in_cpu_threshold=30" \
            -no-color
        working-directory: resources/prod

      # Step 6 — Apply to production
      - name: Terraform Apply
        id: apply
        run: |
          terraform apply \
            -auto-approve \
            -var="aws_region=${{ env.AWS_REGION }}" \
            -var="project_name=mecandjeo-infra" \
            -var="environment=prod" \
            -var="allowed_ssh_cidr=${{ secrets.ALLOWED_SSH_CIDR_PROD }}" \
            -var="vpc_cidr=10.0.0.0/16" \
            -var='public_subnet_cidrs=["10.0.1.0/24","10.0.2.0/24"]' \
            -var='private_subnet_cidrs=["10.0.3.0/24","10.0.4.0/24"]' \
            -var='availability_zones=["us-east-1a","us-east-1b"]' \
            -var="instance_type=t3.micro" \
            -var="container_image=${{ needs.docker.outputs.image_uri }}" \
            -var="container_port=8000" \
            -var="task_cpu=512" \
            -var="task_memory=1024" \
            -var="desired_count=2" \
            -var="health_check_path=/health" \
            -var="min_capacity=2" \
            -var="max_capacity=10" \
            -var="scale_out_cpu_threshold=70" \
            -var="scale_in_cpu_threshold=30" \
            -no-color

          echo "alb_dns_name=$(terraform output -raw alb_dns_name)" \
            >> $GITHUB_OUTPUT
        working-directory: resources/prod

      # Step 7 — Print production deployment summary
      - name: Deployment Summary
        run: |
          echo "══════════════════════════════════════════"
          echo "  PRODUCTION DEPLOYMENT COMPLETE"
          echo "══════════════════════════════════════════"
          echo "  Environment : prod"
          echo "  Image       : ${{ needs.docker.outputs.image_uri }}"
          echo "  Tag         : ${{ needs.docker.outputs.image_tag }}"
          echo "  Commit      : ${{ github.sha }}"
          echo "  Approved by : ${{ github.actor }}"
          echo "  Dashboard   : http://${{ steps.apply.outputs.alb_dns_name }}"
          echo "══════════════════════════════════════════"
```

---

### Step 4: Update `.gitignore`

Confirm `.gitignore` covers plan files:

```bash
# Verify .gitignore has these entries
grep "tfplan" .gitignore || echo "*.tfplan" >> .gitignore
grep "plan-output" .gitignore || echo "plan-output*.txt" >> .gitignore
```

---

### Step 5: Make a Small UI Change to Test the Pipeline

The best way to test the pipeline is to make a visible change to the application and watch it deploy automatically.

Open `apps/mecandjeo-dashboard/static/index.html` and find the footer and update it:

```html
<footer class="footer">
  <span>MecanjeoOps Dashboard — Mecandjeo Technology</span>
  <span>Built with FastAPI · Deployed on AWS ECS Fargate · IaC with Terraform · CI/CD with GitHub Actions</span>
  <span id="last-updated">Last updated: —</span>
</footer>
```

---

### Step 6: Commit and Push Everything

```bash
# Confirm you are in the project root
cd ~/Documents/MY-DEVOPS-WORKS/PROJECTS/vpc-aws-terraform-infra

git add .
git commit -m "Phase 4: Update CI/CD pipeline for real app — builds from Dockerfile, pushes to Docker Hub and ECR"
git push origin main
```

---

### Step 7: Watch the Pipeline Run

1. Go to **github.com/s8mike/aws-terraform-infra**
2. Click **Actions** tab
3. Click the running workflow **MecanjeoOps Dashboard CI/CD**
4. Watch each job run in sequence:
   - `validate` — green ✅
   - `docker` — green ✅
   - `deploy-dev` — green ✅
   - `deploy-prod` — paused ⏸ waiting for approval

---

### Step 8: Verify After Pipeline Completes

```bash
# Get the new ALB DNS from pipeline output or
terraform output alb_dns_name

# Test health endpoint
curl http://YOUR_ALB_DNS/health

# Check ECS tasks
aws ecs describe-services \
  --cluster mecandjeo-infra-dev-cluster \
  --services mecandjeo-infra-dev-service \
  --query "services[0].{Running:runningCount,Desired:desiredCount}" \
  --output table

# Verify new image in ECR
aws ecr describe-images \
  --repository-name mecandjeo-infra-dev \
  --query "imageDetails[*].{Tags:imageTags,Pushed:imagePushedAt}" \
  --output table

# Verify new image on Docker Hub
curl -s \
  "https://hub.docker.com/v2/repositories/s8mike/mecandjeo-dashboard/tags/" \
  | jq -r '.results[].name'
```

Paste the pipeline run result and outputs here and we write the Phase 4 README. 🚀