## Portfolio Phase 4 — CI/CD Pipeline

---

### What We Are Doing in This Phase

We are creating a dedicated GitHub Actions pipeline for the portfolio application. Every push to main that changes portfolio code automatically builds a new Docker image, pushes it to both Docker Hub and ECR, and deploys it to AWS. The portfolio pipeline is completely independent from the dashboard pipeline — they never interfere with each other.

```
Push to main (portfolio files changed)
        │
        ▼
Job 1 — Validate
  ├── terraform fmt -check
  ├── terraform init (portfolio backend)
  ├── terraform validate
  └── terraform plan (reads dashboard remote state)
        │
        ▼
Job 2 — Build and Push Docker Image
  ├── Build from apps/mecandjeo-portfolio/Dockerfile
  ├── Tag with short git SHA
  ├── Push to Docker Hub: s8mike/mecandjeo-portfolio:SHA
  └── Push to ECR: mecandjeo-infra-portfolio:SHA
        │
        ▼
Job 3 — Deploy to Dev (automatic)
  ├── terraform apply with new image URI
  ├── Wait for ECS tasks healthy
  └── Verify /health returns 200
        │
        ▼ ⏸ Manual approval
Job 4 — Deploy to Production
```

---

### Before Writing the Pipeline

Two things to confirm first:

```bash
# 1. Confirm portfolio ECR repository exists
aws ecr describe-repositories \
  --repository-names mecandjeo-infra-portfolio \
  --query "repositories[0].repositoryName" \
  --output text

# 2. Confirm dashboard state has outputs
cd resources/dev
terraform output vpc_id
# Should return a vpc ID not an error
```

Paste both outputs before we write the pipeline. 🚀