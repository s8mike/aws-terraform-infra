
---

**File: `POST-DEPLOYMENT-ACTIVITIES.md`**

```markdown
# Post-Deployment Activities
## MecanjeoOps Infrastructure — Multi-App Platform
**Michael Emmanuel — Mecandjeo Technology — 2026**

---

## 1. Session Workflow

### Prerequisites — Every Session

```bash
# Confirm AWS credentials
aws sts get-caller-identity

# Confirm S3 backend exists
aws s3api head-bucket \
  --bucket mecandjeo-infra-dev-tfstate \
  && echo "Backend ready" \
  || echo "Create bucket — see README prerequisites"

# Confirm ECR images exist
aws ecr describe-images \
  --repository-name mecandjeo-infra-dev \
  --query "imageDetails[*].imageTags" \
  --output table

aws ecr describe-images \
  --repository-name mecandjeo-infra-portfolio \
  --query "imageDetails[*].imageTags" \
  --output table

# Get current IP — update terraform.tfvars if changed
curl ifconfig.me
```

---

### Deploy Shared Infrastructure First

Shared infrastructure must exist before any app deploys.
If already running skip this step.

```bash
cd resources/shared/dev
terraform init
terraform apply -var-file="terraform.tfvars"
# 21 resources — ALL FREE — safe to leave running

# Confirm outputs are available
terraform output
```

---

### Deploy Applications

Each app deploys independently — any order:

```bash
# Dashboard
cd resources/dashboard/dev
terraform init && terraform apply -var-file="terraform.tfvars"
echo "Dashboard: $(terraform output -raw alb_dns_name)"

# Portfolio
cd resources/portfolio/dev
terraform init && terraform apply
echo "Portfolio: $(terraform output -raw portfolio_alb_dns_name)"

# School (pending database setup)
cd resources/school/dev
terraform init && terraform apply -var-file="terraform.tfvars"
echo "School: $(terraform output -raw school_alb_dns_name)"
```

---

### Session End — Destroy to Avoid Charges

Always destroy in reverse dependency order.
Shared infrastructure destroys last.

```bash
# Apps first — any order between them
cd resources/school/dev    && terraform destroy
cd resources/portfolio/dev && terraform destroy
cd resources/dashboard/dev && terraform destroy

# Shared LAST
cd resources/shared/dev    && terraform destroy
```

### Verify Clean Destroy

```bash
# Confirm no ALBs running
aws elbv2 describe-load-balancers \
  --query "LoadBalancers[*].{Name:LoadBalancerName,State:State.Code}" \
  --output table

# Confirm no ECS clusters
aws ecs list-clusters --output table

# Confirm S3 and ECR survived
aws s3 ls s3://mecandjeo-infra-dev-tfstate/ --recursive
aws ecr describe-repositories --output table
```

---

## 2. When to Run What

| Change Type           | Local Action                     | Then                           |
|-----------------------|----------------------------------|--------------------------------|
| App code only         | `docker compose up --build`      | `git push` — pipeline deploys  |
| Infrastructure change | `terraform apply` locally        | `git push` — pipeline confirms |
| Module change         | `terraform apply` locally        | `git push` — all pipelines run |
| New app port          | Update `app_ports`, apply shared | `git push`                     |

**Golden rule:** For application content changes — profile,
skills, projects, CSS, JavaScript — never run `terraform apply`
locally. Just push. The pipeline builds and deploys correctly.

---

## 3. Local Development

```bash
# Dashboard — http://localhost:8000
cd apps/mecandjeo-dashboard
docker compose up --build
docker compose down

# Portfolio — http://localhost:8001
cd apps/mecandjeo-portfolio
docker compose up --build
docker compose down

# School — http://localhost:8002 (requires PostgreSQL)
## Documents/MY-DEVOPS-WORKS/PROJECTS/vpc-aws-terraform-infra/apps/mecandjeo-school 
cd apps/mecandjeo-school
docker compose up --build
docker compose down

# Run this command instead:
uvicorn app.main:app --reload --port 8002
# Uvicorn startup is the authoritative validation
```

---

## 4. Portfolio — Real Content Updates

### What to Change and Where

---

#### Personal Information
**File:** `apps/mecandjeo-portfolio/main.py`
**Section:** `PROFILE` dictionary

Currently populated with real information:
- Name: Michael Emmanuel
- Location: Lagos, Nigeria
- Email: myke7104@gmail.com
- GitHub: github.com/s8mike

**Still needs updating:**
```python
"linkedin": "https://linkedin.com/in/YOUR_REAL_PROFILE",
```

**What changes on browser:** Name in nav, hero typing
animation, bio, location chip, contact links.

---

#### Skill Levels
**File:** `apps/mecandjeo-portfolio/main.py`
**Section:** `SKILLS` list

Adjust `level` values as your skills develop.
Recruiters probe anything above 75.

---

#### Projects
**File:** `apps/mecandjeo-portfolio/main.py`
**Section:** `PROJECTS` list

Currently has 6 projects:
- AWS Multi-App Platform Infrastructure ⭐
- MecanjeoOps Dashboard ⭐
- Multi-App CI/CD Pipeline Automation
- School Platform API
- Monitoring Stack (Prometheus, Grafana, Alertmanager)
- DevOps Automation Tools

Add GitHub links and live URLs as they become available.

---

#### Tool Icons Fix
**File:** `apps/mecandjeo-portfolio/static/app.js`
**Section:** `TOOL_ICONS` object

If icons fail check correct slug at https://simpleicons.org
and update the URL accordingly.

---

#### Background Brightness
**File:** `apps/mecandjeo-portfolio/static/style.css`
**Section:** `:root` CSS variables

```css
/* Lighter — more readable */
--bg:            #0f1623;
--bg-surface:    #141d2e;
--bg-card:       #1a2438;
--bg-card-hover: #1f2d45;
```

---

#### Cache Busting
**File:** `apps/mecandjeo-portfolio/static/index.html`

After significant CSS or JS changes increment version:
```html
<link rel="stylesheet" href="style.css?v=3" />
<script src="app.js?v=3"></script>
```

---

#### Add Experience Timeline
**Files:** `main.py`, `index.html`, `app.js`, `style.css`

Add internship experience at Webforx Technology.
See `REFACTORING-SHARED-INFRASTRUCTURE.md` pending items
for implementation details.

---

## 5. Destroy Order Reference

```
Deploy order:   Shared → Dashboard → Portfolio → School
Destroy order:  School → Portfolio → Dashboard → Shared

Never destroy Shared before apps —
portfolio, dashboard, and school all read
from shared state via terraform_remote_state.
Destroying shared first breaks their remote
state data source.
```

---

## 6. Adding a New Application

```bash
# 1. Create ECR repository
aws ecr create-repository \
  --repository-name mecandjeo-infra-{appname} \
  --image-scanning-configuration scanOnPush=true \
  --region us-east-1

# 2. Add port to security group
# modules/security/main.tf
# app_ports = [8000, 8001, 8002, NEW_PORT]

# 3. Apply shared to update security group
cd resources/shared/dev
terraform apply -var-file="terraform.tfvars"

# 4. Create directories
mkdir -p apps/mecandjeo-{appname}
mkdir -p resources/{appname}/dev

# 5. Build and push image
docker build \
  --file apps/mecandjeo-{appname}/Dockerfile \
  --tag mecandjeo-{appname}:v1.0.0 \
  apps/mecandjeo-{appname}/

docker tag mecandjeo-{appname}:v1.0.0 \
  776735193826.dkr.ecr.us-east-1.amazonaws.com/\
mecandjeo-infra-{appname}:v1.0.0

docker push \
  776735193826.dkr.ecr.us-east-1.amazonaws.com/\
mecandjeo-infra-{appname}:v1.0.0

# 6. Deploy
cd resources/{appname}/dev
terraform init && terraform apply -var-file="terraform.tfvars"
```

---

## 7. Port Assignment

| Application    | Port | Status              |
|----------------|------|---------------------|
| Dashboard      | 8000 | ✅ Live             |
| Portfolio      | 8001 | ✅ Live             |
| School         | 8002 | ⚠️ Pending DB setup |
| Banking        | 8003 | 🔲 Future           |
| Personal CV    | 8004 | 🔲 Future           |
| Small Business | 8005 | 🔲 Future           |
| E-commerce     | 8006 | 🔲 Future           |

---

## 8. School App — Next Steps

The school app infrastructure is deployed and ready.
The app itself requires a PostgreSQL database.

**Option A — SQLite for dev (quickest)**
```python
# apps/mecandjeo-school/app/database.py
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./school.db"
)
```
No infrastructure changes. Data lost on container restart.
Acceptable for dev and testing.

**Option B — RDS PostgreSQL for prod**
Add RDS module to `resources/school/dev/main.tf`.
Pass connection string as ECS environment variable.
~$15/month for `db.t3.micro`.

**Option C — External PostgreSQL (Supabase/Neon)**
Free tier PostgreSQL as a service.
Pass connection string via GitHub Secret → ECS environment.

---

## 9. Troubleshooting Quick Reference

| Symptom                                             | Likely Cause                        | Fix                                        |
|---------------------------------------------------- |-------------------------------------|--------------------------------------------|
| 503 on browser                                      | ECS tasks restarting                | Wait for Running = Desired                 |
| Changes not appearing                               | Old tasks still running       | `force-new-deployment` or push triggers pipeline |
| `remote_state outputs is object with no attributes` | Shared not deployed or no outputs   | Deploy shared, run `terraform output`      |
| `Target.Timeout`                                    | Security group blocking port        | Add port to `app_ports`, apply shared      |
| ALB DNS not resolving                               | Using old DNS from previous session | Run `terraform output` for fresh DNS       |
| `terraform init` network timeout                    | Connectivity issue                  | Copy `.terraform/` from another dir, retry |
| `EntityAlreadyExists` IAM role                      | Pipeline wrong working directory    | Check `working-directory` in pipeline file |



---

## 10. Free Tier Cost Reference

### Always Free

| Resource                            | Cost |
|-------------------------------------|------|
| VPC, subnets, IGW, route tables     | Free |
| Security groups                     | Free |
| IAM roles and policies              | Free |
| S3 state bucket (< 5GB)             | Free |
| ECR repositories (< 500MB/month)    | Free |
| CloudWatch log groups (< 5GB/month) | Free |

### Charged Resources — Destroy After Session

| Resource                             | Cost        |
|--------------------------------------|-------------|
| ALB per instance                     | ~$0.008/hr  |
| ECS Fargate 0.25vCPU/0.5GB per task  | ~$0.004/hr  |
| EC2 t3.micro (after 750hr free tier) | ~$0.0104/hr |

### Approximate Session Cost

```
Shared (21 resources)    : FREE
Dashboard (2 tasks + ALB): ~$0.016/hr
Portfolio (2 tasks + ALB): ~$0.016/hr
School (1 task + ALB)    : ~$0.012/hr
─────────────────────────────────────
All three apps running   : ~$0.044/hr
8-hour session           : ~$0.35
```

Always destroy at end of session.

---

*Built with Terraform on AWS*
*Platform Engineering — Mecandjeo Technology — 2026*
*Stages 1-7 · Dashboard · Portfolio · School Platform*
```

*MecanjeoOps Infrastructure — Post-Deployment Reference*
*Michael Emmanuel — Mecandjeo Technology — 2026*
```

Commit both:

```bash
git add README.md POST-DEPLOYMENT-ACTIVITIES.md
git commit -m "Update: README and POST-DEPLOYMENT-ACTIVITIES reflect shared infrastructure architecture, three apps, Michael Emmanuel"
git push```
---