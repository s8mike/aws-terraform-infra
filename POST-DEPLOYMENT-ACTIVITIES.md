
---

**File: `POST-DEPLOYMENT-ACTIVITIES.md`**

```markdown
# Post-Deployment Activities
## MecanjeoOps Infrastructure — Multi-App Platform
**Mecandjeo Technology — Platform Engineering — 2026**

---

## 1. How to Run Each Application Every Session

### Prerequisites — Run Before Every Session

```bash
# Confirm AWS credentials
aws sts get-caller-identity

# Confirm S3 backend exists
aws s3api head-bucket \
  --bucket mecandjeo-infra-dev-tfstate \
  && echo "Backend ready" \
  || echo "Create bucket first — see README prerequisites"

# Confirm ECR images exist
aws ecr describe-images \
  --repository-name mecandjeo-infra-dev \
  --query "imageDetails[*].imageTags" \
  --output table

aws ecr describe-images \
  --repository-name mecandjeo-infra-portfolio \
  --query "imageDetails[*].imageTags" \
  --output table

# Get current IP — update tfvars if changed
curl ifconfig.me
```

---

### Running the Dashboard

Dashboard deploys shared infrastructure plus its own
ALB and ECS service. Must always be deployed first.

```bash
cd resources/dev
terraform init
terraform apply
echo "Dashboard: $(terraform output -raw alb_dns_name)"
```

---

### Running the Portfolio

Portfolio deploys only 12 resources. Reads shared
infrastructure from dashboard state automatically.
Dashboard must be deployed and outputs written first.

```bash
cd resources/portfolio/dev
terraform init
terraform apply
echo "Portfolio: $(terraform output -raw portfolio_alb_dns_name)"
```

---

### Running Both Together

```bash
# Step 1 — Dashboard first
cd resources/dev
terraform init && terraform apply
echo "Dashboard: $(terraform output -raw alb_dns_name)"

# Step 2 — Portfolio second
cd ../portfolio/dev
terraform init && terraform apply
echo "Portfolio: $(terraform output -raw portfolio_alb_dns_name)"
```

---

### Session End — Destroy to Avoid Charges

Always destroy in reverse order — portfolio first,
dashboard second. Dashboard contains shared infrastructure
that portfolio depends on.

```bash
# Step 1 — Destroy portfolio first
cd resources/portfolio/dev
terraform destroy
# Type yes when prompted

# Step 2 — Destroy dashboard
cd ../dev
terraform destroy
# Type yes when prompted

# Step 3 — Verify S3 and ECR survived
aws s3 ls s3://mecandjeo-infra-dev-tfstate/ --recursive
aws ecr describe-repositories --output table
```

Expected after destroy:
```
S3 bucket        ✅ preserved — outside Terraform
ECR repositories ✅ preserved — outside Terraform
ECR images       ✅ preserved — inside ECR repos
Docker Hub       ✅ preserved — always safe
```

---

### What Survives Every Destroy

| Resource          | Survives | Reason                         |
|-------------------|----------|--------------------------------|
| S3 state bucket   | ✅       | Outside Terraform management  |
| ECR repositories  | ✅       | Outside Terraform management  |
| ECR images        | ✅       | Inside preserved repositories |
| Docker Hub images | ✅       | Always safe                   |
| VPC, ECS, ALB     | ❌       | Destroyed to avoid charges    |

---

## 2. When to Run What — Change Workflow

The correct workflow depends on what type of change
you are making.

| Change Type                                                    | Local Action                        | Then                                        |
|----------------------------------------------------------------|-------------------------------------|---------------------------------------------|
| App code only — `main.py`, `app.js`, `style.css`, `index.html` | `docker compose up --build` to test | `git push` — pipeline deploys automatically |
| Infrastructure — `resources/*/main.tf`, `variables.tf`         | `terraform apply` locally to verify | `git push` — pipeline confirms              |
| Module change — `modules/ecs/main.tf` etc                      | `terraform apply` locally to verify | `git push` — both pipelines run             |
| Both code and infrastructure                                   | `terraform apply` locally first     | `git push` — pipeline handles rest          |

**The golden rule:**
For application content changes — profile, skills, projects,
CSS, JavaScript — never run `terraform apply` locally.
Just push. The pipeline builds the new image and forces
ECS task replacement correctly every time.

---

## 3. Local Development Testing

Always test locally before pushing to verify changes work:

```bash
# Dashboard
cd apps/mecandjeo-dashboard
docker compose up --build
# Open http://localhost:8000
# Test: curl http://localhost:8000/health
docker compose down

# Portfolio
cd apps/mecandjeo-portfolio
docker compose up --build
# Open http://localhost:8001
# Test: curl http://localhost:8001/health
docker compose down
```

---

## 4. Portfolio — Real Content Updates

### What to Change and In Which File

---

#### Change 1 — Personal Information
**File:** `apps/mecandjeo-portfolio/main.py`
**Section:** `PROFILE` dictionary

```python
PROFILE = {
    "name":      "Your Real Full Name",
    "role":      "Platform / DevOps Engineer",
    "tagline":   "Building production-grade infrastructure with AWS · Terraform · Docker",
    "location":  "Your City, Country",
    "email":     "your.real@email.com",
    "github":    "https://github.com/s8mike",
    "linkedin":  "https://linkedin.com/in/your-profile",
    "bio":       (
        "2-3 sentences about yourself. Mention your "
        "internship, AWS and Terraform experience, "
        "and what role you are targeting."
    ),
    "available": True
}
```

**What changes on the browser:**
Name in navigation bar, hero section name and role
typing animation, bio paragraph, location chip,
GitHub button link, footer name, contact section links.

---

#### Change 2 — Skill Levels
**File:** `apps/mecandjeo-portfolio/main.py`
**Section:** `SKILLS` list

Adjust the `level` values to honestly reflect your
actual comfort with each technology. Recruiters will
ask about anything above 75.

```python
SKILLS = [
    { "name": "AWS",            "category": "Cloud",      "level": 75 },
    { "name": "Terraform",      "category": "IaC",        "level": 80 },
    { "name": "Docker",         "category": "Containers", "level": 78 },
    { "name": "GitHub Actions", "category": "CI/CD",      "level": 75 },
    { "name": "Python",         "category": "Languages",  "level": 65 },
    { "name": "Bash / Shell",   "category": "Languages",  "level": 70 },
    # Add or remove skills to match your real experience
]
```

**What changes on the browser:**
Skill card progress bars and percentage labels.

---

#### Change 3 — Projects
**File:** `apps/mecandjeo-portfolio/main.py`
**Section:** `PROJECTS` list

Add real projects from your internship at Webforx
Technology and this infrastructure project:

```python
PROJECTS = [
    {
        "title":       "AWS Multi-App Infrastructure",
        "subtitle":    "Production-grade IaC with Terraform",
        "description": (
            "Designed and provisioned a complete multi-application "
            "AWS infrastructure using Terraform monorepo pattern. "
            "Includes custom VPC, ECS Fargate, ALB, auto scaling, "
            "and remote S3 state management with namespaced keys "
            "for multi-app state isolation. Deployed two applications "
            "simultaneously with independent CI/CD pipelines."
        ),
        "tags":      ["Terraform", "AWS", "ECS", "Docker", "GitHub Actions", "Python"],
        "github":    "https://github.com/s8mike/aws-terraform-infra",
        "live":      "",   # add ALB URL here if you want
        "highlight": True
    },
    {
        "title":       "MecanjeoOps Dashboard",
        "subtitle":    "Live DevOps status dashboard",
        "description": (
            "Real-time DevOps operations dashboard built with "
            "Python FastAPI and vanilla JavaScript. Displays live "
            "system metrics, infrastructure status, service health, "
            "and deployment history. Containerised with Docker and "
            "deployed on AWS ECS Fargate with auto scaling."
        ),
        "tags":      ["Python", "FastAPI", "Docker", "AWS ECS", "ALB"],
        "github":    "https://github.com/s8mike/aws-terraform-infra",
        "live":      "",
        "highlight": True
    },
    {
        "title":       "CI/CD Pipeline Automation",
        "subtitle":    "GitHub Actions — dual registry push",
        "description": (
            "Two independent GitHub Actions pipelines that validate "
            "Terraform code, build Docker images from real Dockerfiles, "
            "push to both Docker Hub and AWS ECR simultaneously, and "
            "deploy to ECS Fargate automatically on every push to main. "
            "Manual approval gate protects production deployments."
        ),
        "tags":      ["GitHub Actions", "Docker", "ECR", "Terraform", "CI/CD"],
        "github":    "https://github.com/s8mike/aws-terraform-infra",
        "live":      "",
        "highlight": False
    },
    # Add projects from your Webforx Technology internship here
]
```

**What changes on the browser:**
Project cards in the projects section — titles,
descriptions, technology tags, GitHub links.

---

#### Change 4 — Tool Icons Fix
**File:** `apps/mecandjeo-portfolio/static/app.js`
**Section:** `TOOL_ICONS` object

Replace the entire `TOOL_ICONS` object with corrected
CDN slugs:

```javascript
const TOOL_ICONS = {
  'AWS':               'https://cdn.simpleicons.org/amazonwebservices/ff9900',
  'ECS Fargate':       'https://cdn.simpleicons.org/amazonwebservices/ff9900',
  'VPC / Networking':  'https://cdn.simpleicons.org/amazonwebservices/ff9900',
  'EC2':               'https://cdn.simpleicons.org/amazonwebservices/ff9900',
  'S3':                'https://cdn.simpleicons.org/amazons3/3f8624',
  'IAM':               'https://cdn.simpleicons.org/amazonwebservices/ff9900',
  'CloudWatch':        'https://cdn.simpleicons.org/amazoncloudwatch/ff4f8b',
  'Terraform':         'https://cdn.simpleicons.org/terraform/7b42bc',
  'Docker':            'https://cdn.simpleicons.org/docker/2496ed',
  'Kubernetes':        'https://cdn.simpleicons.org/kubernetes/326ce5',
  'GitHub Actions':    'https://cdn.simpleicons.org/githubactions/2088ff',
  'CI/CD Pipelines':   'https://cdn.simpleicons.org/githubactions/2088ff',
  'Python':            'https://cdn.simpleicons.org/python/3776ab',
  'Bash / Shell':      'https://cdn.simpleicons.org/gnubash/4eaa25',
  'YAML':              'https://cdn.simpleicons.org/yaml/cb171e',
  'Git':               'https://cdn.simpleicons.org/git/f05032',
  'Linux':             'https://cdn.simpleicons.org/linux/fcc624',
};
```

**What changes on the browser:**
Tool logos in skill cards — AWS orange, Terraform
purple, Docker blue, Python blue etc.

---

#### Change 5 — Background Brightness
**File:** `apps/mecandjeo-portfolio/static/style.css`
**Section:** `:root` CSS variables

Adjust these four values to control darkness:

```css
:root {
  /* Current — very dark */
  --bg:            #080c14;
  --bg-surface:    #0d1220;
  --bg-card:       #111827;
  --bg-card-hover: #151f30;

  /* Lighter option — dark navy */
  --bg:            #0f1623;
  --bg-surface:    #141d2e;
  --bg-card:       #1a2438;
  --bg-card-hover: #1f2d45;

  /* Even lighter — dark slate */
  --bg:            #161b27;
  --bg-surface:    #1c2333;
  --bg-card:       #222d3d;
  --bg-card-hover: #273548;
}
```

**What changes on the browser:**
Background colour of the entire page, hero section,
and skill/project cards.

---

#### Change 6 — Add LinkedIn to Contact
**File:** `apps/mecandjeo-portfolio/main.py`
**Section:** `PROFILE` dictionary — `linkedin` field

```python
"linkedin": "https://linkedin.com/in/your-actual-profile",
```

**File:** `apps/mecandjeo-portfolio/static/app.js`
**Section:** `loadContact` function — `links` array

The LinkedIn link already appears in the contact section
automatically once `PROFILE.linkedin` is set to a real URL.
The filter `.filter(l => !l.href.includes('example'))`
was hiding it because the placeholder URL contained
`yourprofile`. Replace with your real LinkedIn URL and
it appears automatically.

**What changes on the browser:**
LinkedIn link card appears in the contact section.

---

#### Change 7 — Cache Busting After Major Changes
**File:** `apps/mecandjeo-portfolio/static/index.html`
**Section:** `<link>` and `<script>` tags

After making significant CSS or JavaScript changes,
increment the version number to force browsers to
fetch fresh files:

```html
<link rel="stylesheet" href="style.css?v=3" />
...
<script src="app.js?v=3"></script>
```

Increment `v=3` to `v=4` on the next significant change.

**What changes on the browser:**
Clears cached old CSS and JavaScript — ensures all
visitors see the latest version immediately.

---

#### Change 8 — Add Experience Timeline
**File:** `apps/mecandjeo-portfolio/main.py`
**File:** `apps/mecandjeo-portfolio/static/index.html`
**File:** `apps/mecandjeo-portfolio/static/app.js`
**File:** `apps/mecandjeo-portfolio/static/style.css`

Add a new section between Skills and Projects showing
your work history. Requires changes to all four files.

**In `main.py` — add data and endpoint:**
```python
EXPERIENCE = [
    {
        "role":        "Platform Engineering Intern",
        "company":     "Webforx Technology",
        "period":      "2025 — Present",
        "description": (
            "Building production-grade AWS infrastructure "
            "using Terraform and Docker. Deploying containerised "
            "applications on ECS Fargate with automated CI/CD "
            "pipelines using GitHub Actions."
        ),
        "tags": ["AWS", "Terraform", "Docker", "GitHub Actions"]
    }
]

@app.get("/api/experience")
async def get_experience():
    return { "experience": EXPERIENCE }
```

**In `index.html` — add section:**
```html
<!-- Add between skills and projects sections -->
<section class="section section--alt" id="experience">
  <div class="section-inner">
    <div class="section-header">
      <h2 class="section-title">Experience</h2>
      <p class="section-sub">Where I have worked</p>
    </div>
    <div class="experience-timeline"
         id="experience-timeline"></div>
  </div>
</section>
```

**In `app.js` — add loader and call from init:**
```javascript
async function loadExperience() {
  const data = await apiFetch('/api/experience');
  if (!data) return;
  const container = $('experience-timeline');
  container.innerHTML = '';
  data.experience.forEach(exp => {
    const item = document.createElement('div');
    item.className = 'experience-item fade-in';
    item.innerHTML = `
      <div class="exp-role">${exp.role}</div>
      <div class="exp-company">${exp.company}</div>
      <div class="exp-period">${exp.period}</div>
      <p class="exp-desc">${exp.description}</p>
      <div class="exp-tags">
        ${exp.tags.map(t =>
          `<span class="project-tag">${t}</span>`
        ).join('')}
      </div>
    `;
    container.appendChild(item);
  });
}

// Add to init() function:
async function init() {
  initHeroCanvas();
  await Promise.all([
    loadProfile(),
    loadSkills(),
    loadExperience(),  // add this line
    loadProjects(),
    loadContact(),
  ]);
  initScrollFadeIn();
}
```

**In `style.css` — add styles:**
```css
.experience-timeline {
  display: flex;
  flex-direction: column;
  gap: 20px;
  max-width: 800px;
  margin: 0 auto;
}

.experience-item {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-left: 3px solid var(--blue);
  border-radius: var(--radius-sm);
  padding: 24px 28px;
  transition: all var(--transition);
}

.experience-item:hover {
  border-left-color: var(--blue-bright);
  background: var(--bg-card-hover);
  transform: translateX(4px);
}

.exp-role {
  font-size: 17px;
  font-weight: 700;
  color: var(--text);
  margin-bottom: 4px;
}

.exp-company {
  font-size: 14px;
  font-weight: 600;
  color: var(--blue-bright);
  margin-bottom: 4px;
  font-family: 'JetBrains Mono', monospace;
}

.exp-period {
  font-size: 12px;
  color: var(--text-dim);
  margin-bottom: 12px;
  font-family: 'JetBrains Mono', monospace;
}

.exp-desc {
  font-size: 14px;
  color: var(--text-muted);
  line-height: 1.7;
  margin-bottom: 14px;
}

.exp-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
```

---

## 5. Suggested Applications to Build Next

Each new application follows the same four-phase pattern.

| App                 | Port | Stack                   | New AWS Resource     |
|---------------------|------|-------------------------|----------------------|
| Banking demo        | 8002 | FastAPI + DynamoDB      | DynamoDB table       |
| School management   | 8003 | FastAPI + DynamoDB      | DynamoDB table       |
| Personal CV / bio   | 8004 | FastAPI + HTML/CSS      | None                 |
| Small business site | 8005 | FastAPI + HTML/CSS      | None                 |
| E-commerce store    | 8006 | FastAPI + DynamoDB + S3 | DynamoDB + S3 assets |

### Adding a New App — Quick Checklist

```bash
# 1. Create ECR repository
aws ecr create-repository \
  --repository-name mecandjeo-infra-{appname} \
  --image-scanning-configuration scanOnPush=true \
  --region us-east-1

# 2. Add port to security group
# modules/security/main.tf
# app_ports = [8000, 8001, NEW_PORT]

# 3. Create app directory
mkdir -p apps/mecandjeo-{appname}/static
mkdir -p resources/{appname}/dev

# 4. Create pipeline file
touch .github/workflows/{appname}-cicd.yml

# 5. Deploy dashboard first — then new app
```

---

## 6. Clean Destroy Procedure — Multi-App

### Why Order Matters

The portfolio reads outputs from the dashboard state via
`terraform_remote_state`. If you destroy the dashboard
first the portfolio state becomes orphaned — its remote
state data source can no longer resolve.

Always destroy in reverse dependency order:

```
Deploy order:   Dashboard → Portfolio → Banking → School
Destroy order:  School → Banking → Portfolio → Dashboard
```

### Full Clean Destroy

```bash
# Step 1 — Destroy portfolio (depends on dashboard)
cd resources/portfolio/dev
terraform destroy
# Type yes

# Step 2 — Confirm portfolio is gone
aws ecs describe-clusters \
  --clusters mecandjeo-portfolio-dev-cluster \
  --query "clusters[0].status" \
  --output text 2>/dev/null || echo "DELETED ✅"

# Step 3 — Destroy dashboard (shared infra)
cd ../dev
terraform destroy
# Type yes

# Step 4 — Confirm dashboard is gone
aws ecs describe-clusters \
  --clusters mecandjeo-infra-dev-cluster \
  --query "clusters[0].status" \
  --output text 2>/dev/null || echo "DELETED ✅"

# Step 5 — Verify S3 and ECR survived
echo "=== S3 State Keys ===" && \
aws s3 ls s3://mecandjeo-infra-dev-tfstate/ --recursive && \
echo "=== ECR Repositories ===" && \
aws ecr describe-repositories \
  --query "repositories[*].repositoryName" \
  --output table

# Step 6 — Verify no running charges
echo "=== ALB Check ===" && \
aws elbv2 describe-load-balancers \
  --query "LoadBalancers[*].{Name:LoadBalancerName,State:State.Code}" \
  --output table 2>/dev/null || echo "No ALBs running ✅"
```

### What the S3 Bucket Should Show After Full Destroy

```
mecandjoe-infra-dev-tfstate/
├── mecandjeo-dashboard/dev/terraform.tfstate   ← empty state
├── mecandjeo-portfolio/dev/terraform.tfstate   ← empty state
└── school-platform/dev/terraform.tfstate       ← separate repo
```

The state files remain — they are just empty after destroy.
The S3 bucket itself is preserved. ECR repositories and
images are preserved. Only AWS compute resources are gone.

---

## 7. Free Tier Cost Reference

### Always Free

| Resource                            | Cost |
|-------------------------------------|------|
| VPC, subnets, IGW, route tables     | Free |
| Security groups                     | Free |
| IAM roles and policies              | Free |
| S3 state bucket (< 5GB)             | Free |
| ECR repositories (< 500MB/month)    | Free |
| CloudWatch log groups (< 5GB/month) | Free |

### Charged Resources — Destroy After Every Session

| Resource                            | Cost                   | Destroy Command     |
|-------------------------------------|------------------------|---------------------|
| ALB per instance                    | ~$0.008/hr             | `terraform destroy` |
| ECS Fargate 0.25vCPU/0.5GB per task | ~$0.004/hr             | `terraform destroy` |
| EC2 t3.micro                        | Free tier 750hrs/month | `terraform destroy` |

### Cost Per Session — Both Apps Running

```
Dashboard ALB        : $0.008/hr
Portfolio ALB        : $0.008/hr
Dashboard ECS x2     : $0.008/hr
Portfolio ECS x2     : $0.008/hr
EC2 t3.micro         : free tier
─────────────────────────────────
Total                : ~$0.032/hr
8-hour session       : ~$0.26
Left running 24hrs   : ~$0.77/day
```

Always destroy at the end of every session.

---

## 8. Troubleshooting Quick Reference

### 503 Service Unavailable
ECS tasks are restarting or unhealthy.
```bash
aws ecs describe-services \
  --cluster mecandjeo-portfolio-dev-cluster \
  --services mecandjeo-portfolio-dev-service \
  --query "services[0].{Running:runningCount,Desired:desiredCount}" \
  --output table
# Wait for Running = Desired then refresh browser
```

### Changes Not Appearing After Push
Pipeline ran but ECS still serving old image.
```bash
# Check pipeline completed in GitHub Actions
# Then check tasks are running new image
aws ecs describe-services \
  --cluster mecandjeo-portfolio-dev-cluster \
  --services mecandjeo-portfolio-dev-service \
  --query "services[0].deployments" \
  --output json
# Look for PRIMARY deployment with runningCount = desiredCount
```

### terraform_remote_state No Outputs
Dashboard not deployed or outputs not written.
```bash
cd resources/dev
terraform output
# If empty — run terraform apply to write outputs
```

### Target.Timeout Health Check Failure
Security group blocking the container port.
```bash
# Check app_ports list in modules/security/main.tf
# Confirm new app port is in the list
# Apply dashboard to update security group
```

### ALB DNS Not Resolving
Using old DNS name from previous session.
```bash
terraform output alb_dns_name
# Always get fresh DNS after every apply
```

---

*MecanjeoOps Infrastructure — Post-Deployment Reference*
*Mecandjeo Technology — Platform Engineering — 2026*
```

---

Commit this file:

```bash
git add POST-DEPLOYMENT-ACTIVITIES.md
git commit -m "Add: POST-DEPLOYMENT-ACTIVITIES.md — session workflow, portfolio content guide, destroy procedure, troubleshooting"
git push
```

---

### Now — Portfolio Real Content Updates

Share the following and I will write the complete updated `main.py` in one shot:

1. **Your real full name**
2. **Your real location** — city and country
3. **Your real email**
4. **Your LinkedIn URL**
5. **Your bio** — 2-3 sentences about yourself
6. **Skill levels** — rate each honestly 1-100
7. **Any real projects from Webforx Technology** to add

Once you share these I write the complete file, you paste it in, test locally, push, and the pipeline deploys everything automatically. 🚀