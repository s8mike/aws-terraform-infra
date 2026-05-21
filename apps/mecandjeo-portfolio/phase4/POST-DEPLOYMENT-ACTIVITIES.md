
---

**File: `POST-DEPLOYMENT-ACTIVITIES.md`**

---

```markdown
# Post-Deployment Activities
## MecanjeoOps Infrastructure — Multi-App Platform
**Mecandjeo Technology — Platform Engineering**

---

## 1. How to Run Each Application

### Prerequisites — Run Before Every Session

```bash
# Confirm AWS credentials are active
aws sts get-caller-identity

# Confirm S3 backend bucket exists
aws s3api head-bucket \
  --bucket mecandjeo-infra-dev-tfstate \
  && echo "Backend ready" \
  || echo "Create bucket first"

# Confirm ECR images exist
aws ecr describe-images \
  --repository-name mecandjeo-infra-dev \
  --query "imageDetails[*].imageTags" \
  --output table

aws ecr describe-images \
  --repository-name mecandjeo-infra-portfolio \
  --query "imageDetails[*].imageTags" \
  --output table

# Get your current IP — update tfvars if changed
curl ifconfig.me
```

---

### Running the Dashboard

The dashboard includes all shared infrastructure — VPC, security groups,
IAM, EC2 — plus its own ALB and ECS service. It must always be deployed
first because the portfolio reads its outputs.

```bash
cd resources/dev

# Initialise
terraform init

# Preview
terraform plan

# Deploy — 31 resources
terraform apply

# Get the live URL
terraform output alb_dns_name
```

Expected outputs:
```
alb_dns_name                = "mecandjeo-infra-dev-alb-XXXXXX.us-east-1.elb.amazonaws.com"
alb_security_group_id       = "sg-XXXXXXXXX"
ecs_security_group_id       = "sg-XXXXXXXXX"
ecs_task_execution_role_arn = "arn:aws:iam::776735193826:role/..."
public_subnet_ids           = ["subnet-XXXXX", "subnet-XXXXX"]
vpc_id                      = "vpc-XXXXXXXXX"
```

Verify dashboard is live:
```bash
curl http://$(terraform output -raw alb_dns_name)/health
```

---

### Running the Portfolio

The portfolio deploys only 12 resources — ALB, ECS, autoscaling.
It reads VPC and security values from the dashboard state automatically.
**Dashboard must be deployed and outputs written before running portfolio.**

```bash
cd resources/portfolio/dev

# Initialise
terraform init

# Preview — reads dashboard remote state
terraform plan

# Deploy — 12 resources
terraform apply

# Get the live URL
terraform output portfolio_alb_dns_name
```

Verify portfolio is live:
```bash
curl http://$(terraform output -raw portfolio_alb_dns_name)/health
```

---

### Running Both Applications Together

```bash
# Step 1 — Deploy dashboard first (shared infra + dashboard)
cd resources/dev
terraform init && terraform apply
echo "Dashboard: $(terraform output -raw alb_dns_name)"

# Step 2 — Deploy portfolio (reads from dashboard state)
cd ../portfolio/dev
terraform init && terraform apply
echo "Portfolio: $(terraform output -raw portfolio_alb_dns_name)"
```

---

### Session End — Destroy to Avoid Charges

```bash
# Destroy portfolio first (depends on dashboard)
cd resources/portfolio/dev
terraform destroy

# Then destroy dashboard
cd ../dev  
terraform destroy
```

What survives destroy:
```
S3 state bucket         ✅ permanent — outside Terraform
ECR repositories        ✅ permanent — outside Terraform
ECR images              ✅ permanent — inside ECR repos
Docker Hub images       ✅ permanent — always safe
```

---

### Running Local Development

Test application changes locally before pushing:

```bash
# Dashboard
cd apps/mecandjeo-dashboard
docker compose up --build
# Open http://localhost:8000

# Portfolio
cd apps/mecandjeo-portfolio
docker compose up --build
# Open http://localhost:8001

# Stop when done
docker compose down
```

---

## 2. CI/CD Pipeline — How Changes Deploy Automatically

Every push to main triggers the relevant pipeline automatically.
No manual deployment needed after the initial session setup.

### Dashboard Pipeline Triggers
```
Change apps/mecandjeo-dashboard/**  → dashboard pipeline
Change modules/**                   → both pipelines
Change resources/dev/**             → dashboard pipeline
```

### Portfolio Pipeline Triggers
```
Change apps/mecandjeo-portfolio/**  → portfolio pipeline
Change modules/**                   → both pipelines
Change resources/portfolio/**       → portfolio pipeline
```

### Standard Change Workflow

```bash
# 1. Make changes locally
# 2. Test with docker compose
# 3. Commit and push
git add .
git commit -m "description of change"
git push origin main
# 4. Watch pipeline in GitHub Actions
# 5. Get new ALB DNS from pipeline summary or terraform output
```

---

## 3. Portfolio — Real Content Updates

These changes update the portfolio with real personal information.
Each change triggers the portfolio pipeline and deploys automatically.

### Update 1 — Personal Information

Open `apps/mecandjeo-portfolio/main.py` and update the `PROFILE` dictionary:

```python
PROFILE = {
    "name":      "Your Real Full Name",
    "role":      "Platform / DevOps Engineer",
    "tagline":   "Building production-grade infrastructure with AWS · Terraform · Docker",
    "location":  "Lagos, Nigeria",
    "email":     "your.real.email@gmail.com",
    "github":    "https://github.com/s8mike",
    "linkedin":  "https://linkedin.com/in/your-real-profile",
    "bio":       (
        "Write 2-3 sentences about yourself here. "
        "Mention your internship at Webforx Technology, "
        "your AWS and Terraform experience, and what you "
        "are looking for in your next role."
    ),
    "available": True   # set False when not job hunting
}
```

Commit and push — portfolio pipeline deploys the update automatically.

---

### Update 2 — Skills — Adjust Levels to Reflect Reality

Open `apps/mecandjeo-portfolio/main.py` and update `SKILLS`.
Be honest with skill levels — recruiters will ask about them:

```python
SKILLS = [
    # Set levels based on real comfort — 60-70 is solid,
    # 80+ means you can be interviewed deeply on it
    { "name": "AWS",            "category": "Cloud",      "level": 75 },
    { "name": "Terraform",      "category": "IaC",        "level": 80 },
    { "name": "Docker",         "category": "Containers", "level": 78 },
    { "name": "GitHub Actions", "category": "CI/CD",      "level": 75 },
    { "name": "Python",         "category": "Languages",  "level": 65 },
    # Add any missing skills from your actual work
]
```

---

### Update 3 — Add Real Projects

Update the `PROJECTS` list with real work from your internship
and personal projects. Each project should have a live URL if
it is deployed:

```python
PROJECTS = [
    {
        "title":       "AWS Auto-Scaling Infrastructure",
        "subtitle":    "Production-grade IaC with Terraform",
        "description": (
            "Designed and provisioned a complete multi-application "
            "AWS infrastructure using Terraform monorepo pattern. "
            "Includes custom VPC, ECS Fargate, ALB, auto scaling, "
            "and remote S3 state management with namespaced keys. "
            "Deployed two applications simultaneously with independent "
            "CI/CD pipelines."
        ),
        "tags":    ["Terraform", "AWS", "ECS", "Docker", "GitHub Actions"],
        "github":  "https://github.com/s8mike/aws-terraform-infra",
        "live":    "http://YOUR_DASHBOARD_ALB_DNS",  # add real URL
        "highlight": True
    },
    # Add projects from your internship at Webforx Technology
    {
        "title":       "Project Name from Internship",
        "subtitle":    "Brief tech description",
        "description": "What you built, what problem it solved...",
        "tags":        ["relevant", "technologies"],
        "github":      "https://github.com/s8mike/repo-name",
        "live":        "",
        "highlight":   True
    },
]
```

---

### Update 4 — Fix AWS Tool Icons

Open `apps/mecandjeo-portfolio/static/app.js` and find the
`TOOL_ICONS` map. The AWS icons need corrected CDN slugs:

```javascript
const TOOL_ICONS = {
  'AWS':               'https://cdn.simpleicons.org/amazonwebservices/ff9900',
  'ECS Fargate':       'https://cdn.simpleicons.org/amazonwebservices/ff9900',
  'VPC / Networking':  'https://cdn.simpleicons.org/amazonwebservices/ff9900',
  'EC2':               'https://cdn.simpleicons.org/amazonwebservices/ff9900',
  'S3':                'https://cdn.simpleicons.org/amazons3/3f8624',
  'IAM':               'https://cdn.simpleicons.org/amazonwebservices/ff9900',
  'CloudWatch':        'https://cdn.simpleicons.org/amazoncloudwatch/ff4f8b',
  'Terraform':         'https://cdn.simpleicons.org/terraform/844FBA',
  'Docker':            'https://cdn.simpleicons.org/docker/2496ED',
  'Kubernetes':        'https://cdn.simpleicons.org/kubernetes/326CE5',
  'GitHub Actions':    'https://cdn.simpleicons.org/githubactions/2088FF',
  'CI/CD Pipelines':   'https://cdn.simpleicons.org/githubactions/2088FF',
  'Python':            'https://cdn.simpleicons.org/python/3776AB',
  'Bash / Shell':      'https://cdn.simpleicons.org/gnubash/4EAA25',
  'YAML':              'https://cdn.simpleicons.org/yaml/CB171E',
  'Git':               'https://cdn.simpleicons.org/git/F03C2E',
  'Linux':             'https://cdn.simpleicons.org/linux/fCC624',
};
```

If icons still fail after this update the CDN slug has changed.
Check the correct slug at https://simpleicons.org — search for
the tool name and copy the slug from the URL.

---

### Update 5 — Adjust Background Brightness

If the dark background feels too dark or too light open
`apps/mecandjeo-portfolio/static/style.css` and adjust
the CSS variables in the `:root` block:

```css
:root {
  /* Darker — more dramatic */
  --bg:            #080c14;
  --bg-surface:    #0d1220;
  --bg-card:       #111827;

  /* Lighter — more readable */
  --bg:            #0f1623;
  --bg-surface:    #141d2e;
  --bg-card:       #1a2438;

  /* Even lighter — closer to dark grey */
  --bg:            #161b27;
  --bg-surface:    #1c2333;
  --bg-card:       #222d3d;
}
```

Push and watch the pipeline deploy the colour change within minutes.

---

### Update 6 — Add Profile Photo

To replace the letter avatar with a real photo:

**Step 1 — Add photo to static folder:**
```bash
# Copy your photo to the static directory
cp your-photo.jpg apps/mecandjeo-portfolio/static/avatar.jpg
```

**Step 2 — Update `index.html`:**
```html
<!-- Replace this -->
<div class="hero-avatar" id="hero-avatar">M</div>

<!-- With this -->
<div class="hero-avatar" id="hero-avatar">
  <img src="avatar.jpg" alt="Profile photo"
       style="width:100%;height:100%;
              object-fit:cover;border-radius:50%;" />
</div>
```

**Step 3 — Remove the avatar letter population in `app.js`:**
```javascript
// Comment out or remove this line in loadProfile()
// $('hero-avatar').textContent = data.name.charAt(0).toUpperCase();
```
# to continue further improvementd from here below.
---

### Update 7 — Add Experience Timeline Section

Add a new section between Skills and Projects showing your
work history. Requires changes to all three files.

**In `main.py` — add experience data and endpoint:**
```python
EXPERIENCE = [
    {
        "role":        "Platform Engineering Intern",
        "company":     "Webforx Technology",
        "period":      "2025 — Present",
        "description": "Building production-grade AWS infrastructure...",
        "tags":        ["AWS", "Terraform", "Docker", "GitHub Actions"]
    }
]

@app.get("/api/experience")
async def get_experience():
    return { "experience": EXPERIENCE }
```

**In `index.html` — add the section between skills and projects:**
```html
<section class="section" id="experience">
  <div class="section-inner">
    <div class="section-header">
      <h2 class="section-title">Experience</h2>
    </div>
    <div class="experience-timeline" id="experience-timeline"></div>
  </div>
</section>
```

**In `app.js` — add the loader:**
```javascript
async function loadExperience() {
  const data = await apiFetch('/api/experience');
  if (!data) return;
  const container = $('experience-timeline');
  data.experience.forEach(exp => {
    const item = document.createElement('div');
    item.className = 'experience-item';
    item.innerHTML = `
      <div class="exp-role">${exp.role}</div>
      <div class="exp-company">${exp.company}</div>
      <div class="exp-period">${exp.period}</div>
      <p class="exp-desc">${exp.description}</p>
    `;
    container.appendChild(item);
  });
}
// Add to init(): await loadExperience();
```

---

## 4. Suggested Applications to Build Next

Each application follows the same four-phase pattern:
Phase 1 — Build locally, Phase 2 — Push to registries,
Phase 3 — Deploy with Terraform, Phase 4 — Wire CI/CD.

---

### App 3 — Banking Demo Application

**Purpose:** Demonstrates a multi-tier application with a database,
authentication, and financial transaction logic. Highly relevant
for fintech roles.

**Stack:** Python FastAPI + DynamoDB + AWS Cognito (optional)

**New Infrastructure Required:**
```hcl
# New modules needed:
module "dynamodb" { ... }   # transaction table
module "cognito"  { ... }   # user authentication (optional)
```

**Port:** 8002

**Key Features:**
- User account dashboard
- Transaction history
- Balance display
- Transfer simulation
- DynamoDB for persistence

**State Key:**
```
mecandjeo-banking/dev/terraform.tfstate
```

**ECR Repository:**
```bash
aws ecr create-repository \
  --repository-name mecandjeo-infra-banking \
  --region us-east-1
```

---

### App 4 — School Management Application

**Purpose:** Demonstrates a CRUD application with multiple
data entities — students, courses, grades. Relevant for
education sector roles.

**Stack:** Python FastAPI + DynamoDB (or RDS PostgreSQL)

**Port:** 8003

**Key Features:**
- Student registration
- Course enrollment
- Grade management
- Attendance tracking
- Admin dashboard

**State Key:**
```
mecandjeo-school/dev/terraform.tfstate
```

**Note:** You already have `school-platform/dev/terraform.tfstate`
in the S3 bucket from a separate repo. When you migrate it to
this infrastructure use key `mecandjeo-school/dev/terraform.tfstate`
for consistency.

---

### App 5 — Personal Bio / CV Application

**Purpose:** A single-page CV application with downloadable PDF.
Simple to build, immediately useful for job applications.

**Stack:** Python FastAPI + HTML/CSS

**Port:** 8004

**Key Features:**
- Clean CV layout
- Downloadable PDF via endpoint
- Print-optimised CSS
- QR code linking to GitHub

**State Key:**
```
mecandjeo-bio/dev/terraform.tfstate
```

---

### App 6 — Small Business Website

**Purpose:** A template business website demonstrating
frontend skills and content management patterns.

**Stack:** Python FastAPI + HTML/CSS/JS

**Port:** 8005

**Key Features:**
- Landing page with hero
- Services section
- Team section
- Contact form
- Google Maps embed

---

### App 7 — E-Commerce Store (Advanced)

**Purpose:** Full e-commerce demonstration with product catalog,
cart, and checkout flow. Highly impressive for senior roles.

**Stack:** Python FastAPI + DynamoDB + S3 (product images)

**New Infrastructure Required:**
```hcl
module "s3_assets" { ... }    # product images bucket
module "dynamodb"  { ... }    # products and orders tables
module "cloudfront"{ ... }    # CDN for static assets (optional)
```

**Port:** 8006

---

## 5. Implementing Shared Infrastructure — Impact and Plan

### What This Means

Currently the dashboard state (`resources/dev/`) bundles two
concerns together:

```
resources/dev/main.tf contains:
  ├── Shared infrastructure (VPC, subnets, security groups, IAM, EC2)
  │   └── These are FREE — no cost to leave running
  └── Dashboard application (ALB, ECS, autoscaling)
      └── These COST MONEY — destroy between sessions
```

The goal is to separate them so shared infrastructure can
stay running permanently at zero cost while application
resources are created and destroyed per session.

---

### Impact on Current State

**This is a breaking change that requires careful migration.**

| Resource            | Current Location           | After Migration                        |
|---------------------|----------------------------|----------------------------------------|
| VPC, subnets, IGW   | `resources/dev/`           | `resources/shared/dev/`                |
| Security groups     | `resources/dev/`           | `resources/shared/dev/`                |
| IAM roles           | `resources/dev/`           | `resources/shared/dev/`                |
| EC2 instance        | `resources/dev/`           | `resources/shared/dev/`                |
| Dashboard ALB + ECS | `resources/dev/`           | `resources/dashboard/dev/`             |
| Portfolio ALB + ECS | `resources/portfolio/dev/` | `resources/portfolio/dev/` (unchanged) |

The migration requires:
1. `terraform state mv` to move resources between state files
2. Updating `main.tf` files to remove moved resources
3. Creating new `resources/shared/dev/` configuration
4. Updating all `terraform_remote_state` references
5. Updating the dashboard pipeline working directory

---

### Target Directory Structure

```
resources/
├── shared/
│   ├── dev/
│   │   ├── main.tf          ← VPC, security, IAM, EC2
│   │   ├── backend.tf       ← key: mecandjeo-shared/dev/terraform.tfstate
│   │   ├── variables.tf
│   │   └── terraform.tfvars.pipeline
│   └── prod/
│       └── ...
│
├── dashboard/
│   ├── dev/
│   │   ├── main.tf          ← ALB, ECS, autoscaling only
│   │   ├── backend.tf       ← key: mecandjeo-dashboard/dev/terraform.tfstate
│   │   └── ...              ← reads from shared state
│   └── prod/
│       └── ...
│
└── portfolio/
    ├── dev/                  ← already correct structure
    │   ├── main.tf           ← reads from shared state
    │   └── ...
    └── prod/
        └── ...
```

---

### New S3 Bucket Structure After Migration

```
mecandjeo-infra-dev-tfstate/
├── mecandjeo-shared/dev/terraform.tfstate       ← free resources, permanent
├── mecandjeo-dashboard/dev/terraform.tfstate    ← dashboard only
├── mecandjeo-portfolio/dev/terraform.tfstate    ← portfolio only
├── mecandjeo-banking/dev/terraform.tfstate      ← future
└── mecandjeo-school/dev/terraform.tfstate       ← future
```

---

### New Session Workflow After Migration

```bash
# First time only — or after full destroy
cd resources/shared/dev
terraform apply   # deploys VPC, security, IAM, EC2
# Leave running — ZERO COST

# Every session — deploy only the app you need
cd resources/dashboard/dev
terraform apply   # deploys only dashboard ALB + ECS (12 resources)
open $(terraform output -raw alb_dns_name)

# OR deploy portfolio
cd resources/portfolio/dev
terraform apply   # deploys only portfolio ALB + ECS (12 resources)
open $(terraform output -raw portfolio_alb_dns_name)

# End of session — destroy only app resources
cd resources/dashboard/dev && terraform destroy
cd resources/portfolio/dev && terraform destroy
# Shared infra stays running — VPC, security groups, IAM = FREE
```

---

### Benefits After Migration

| Scenario              | Current                         | After Migration                    |
|-----------------------|---------------------------------|------------------------------------|
| Session start time    | Deploy 31 resources (~5 min)    | Deploy 12 resources (~2 min)       |
| Session end           | Destroy 31 + 12 resources       | Destroy 12 resources only          |
| Deploy portfolio only | Must deploy dashboard first     | Deploy shared once, then portfolio |
| Add new application   | Dashboard must exist            | Shared infra already running       |
| Overnight cost        | All destroyed, rebuild next day | Shared stays up, free              |
| Destroy risk          | One mistake destroys all        | Apps isolated from shared infra    |

---

### Migration Plan — When to Do It

**Do not migrate now.** The safest time to migrate is when:

1. All current resources are destroyed (clean state)
2. You have at least 2 hours uninterrupted
3. You have tested the `terraform state mv` commands locally first

**Recommended trigger:** When you start building App 3 (banking).
At that point the shared infrastructure pattern becomes clearly
worth the migration effort.

**Migration steps when ready:**
```bash
# Step 1 — Destroy everything first
cd resources/portfolio/dev && terraform destroy
cd resources/dev && terraform destroy

# Step 2 — Create resources/shared/dev/ with VPC and security modules
# Step 3 — Create resources/dashboard/dev/ with ALB and ECS modules only
# Step 4 — Deploy shared first, then dashboard, then portfolio
# Step 5 — Update both pipelines with new working directories
# Step 6 — Update terraform_remote_state references in dashboard and portfolio
```

---

## 6. Free Tier Cost Reference

### Resources That Are Always Free

| Resource                      | Cost |
|-------------------------------|------|
| VPC                           | Free |
| Subnets (up to 200)           | Free |
| Internet Gateway              | Free |
| Route Tables                  | Free |
| Security Groups               | Free |
| IAM Roles and Policies        | Free |
| S3 state bucket (< 5GB)       | Free |
| ECR repositories (< 500MB)    | Free |
| CloudWatch Log Groups (< 5GB) | Free |

### Resources With Free Tier Limits

| Resource                       | Free Tier     | After Free Tier          |
|--------------------------------|---------------|--------------------------|
| EC2 t3.micro                   | 750 hrs/month | ~$0.0104/hr              |
| ECS Fargate (0.25 vCPU, 0.5GB) | None          | ~$0.004/hr per task      |
| ALB                            | None          | ~$0.008/hr + LCU charges |

### Cost Per Session (Both Apps Running)

```
Dashboard ALB     : $0.008/hr
Portfolio ALB     : $0.008/hr
Dashboard ECS x2  : $0.008/hr
Portfolio ECS x1  : $0.004/hr
EC2 t3.micro      : free tier (750 hrs/month)
─────────────────────────────────
Total             : ~$0.028/hr (~$0.67/day if left running)
```

Always destroy at the end of every session while on free tier.

---

*MecanjeoOps Infrastructure — Post-Deployment Reference*
*Mecandjeo Technology — Platform Engineering — 2026*
```

---

Commit this file:

```bash
git add POST-DEPLOYMENT-ACTIVITIES.md
git commit -m "Add: post-deployment activities, real content updates, future app suggestions, shared infra migration plan"
git push
```

Ready for the **Final Project README update** whenever you are. 🚀