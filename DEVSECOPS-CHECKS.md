# DevSecOps Tool Usage Guide

## Tool Installation Recommendation

For Windows-based DevOps and Cloud Engineering workstations, install system-level tools using **Windows PowerShell (Run as Administrator)** rather than Git Bash.

Examples include:

* Terraform
* AWS CLI
* kubectl
* Helm
* Minikube
* Docker Desktop
* Trivy
* TFLint
* tfsec
* Gitleaks
* Checkov
* Python packages installed globally

### Why PowerShell is Recommended

Most Windows package managers and installers are designed to work natively with Windows environments:

* Chocolatey (`choco`)
* Winget (`winget`)
* MSI installers
* Python installers

These tools often:

* Write to protected system directories
* Modify Windows PATH variables
* Create executable shims (`.exe`, `.cmd`)
* Require elevated permissions

PowerShell handles these operations more reliably than Git Bash.

### Recommended Workflow

1. Open **PowerShell as Administrator**.
2. Install tools using `winget`, `choco`, or `pip`.
3. Verify the installation in PowerShell.
4. Open Git Bash and verify the command is available.
5. Use either PowerShell or Git Bash for daily development work.

### Example

Install:

```powershell
choco install minikube -y
python -m pip install checkov
```

Verify:

```powershell
minikube version
python -m checkov.main --version
```

Then test in Git Bash:

```bash
minikube version
python -m checkov.main --version
```

### Key Principle

**Install in PowerShell, verify in PowerShell, then consume from Git Bash if desired.**

This approach minimizes Windows permission issues, PATH problems, executable shim errors, and package installation failures while still allowing Git Bash to be used as the primary development terminal.


Git Bash is an excellent daily working terminal for Terraform, Git, AWS CLI, kubectl, and scripting. However, PowerShell should be treated as the authoritative installation and troubleshooting environment on Windows. When a tool behaves differently between the two shells, verify it in PowerShell first before assuming the installation is broken.



## General Rule to Run Checks

Navigate to the root of the repository before running scans.
Most tools need to see the full project structure to resolve
module references, relative paths, and configuration files.

Example:

```bash
cd ~/Documents/MY-DEVOPS-WORKS/PROJECTS/vpc-aws-terraform-infra
```

or

# PowerShell
cd C:\Users\Home\Documents\MY-DEVOPS-WORKS\PROJECTS\vpc-aws-terraform-infra
```

```
## Ignore Files — How They Work

Three ignore files live at the project root. Each tells a
different tool which findings to suppress. Every suppressed
finding must have a documented reason — tool, CVE ID, why
the risk is accepted, and when to revisit.

| File                | Tool      | Purpose                                            |
|---------------------|-----------|----------------------------------------------------|
| `.trivyignore`      | trivy     | Suppress OS and package CVEs with no fix available |
| `.pip-audit-ignore` | pip-audit | Suppress Python dependency CVEs blocked by version constraints |
| `# checkov:skip`    | checkov   | Inline suppression comments in `.tf` files         |

### `.trivyignore` — Example Entry
```
# perl-base CRITICAL — no fix available in Debian 13 as of June 2026
# Status: fix_deferred — Debian has not yet released a patched package
# Revisit monthly — check https://security-tracker.debian.org
CVE-2026-42496
```

### `.pip-audit-ignore` — Example Entry
```
# starlette DoS — fix requires starlette>=0.49.1
# Conflicts with fastapi==0.115.12 which pins starlette<0.47.0
# App has no Range-header responses — attack surface is zero
# Revisit when FastAPI supports starlette>=0.49.x
CVE-2025-62727
```

### `checkov:skip` — Example Inline Comment
```hcl
resource "aws_lb" "main" {
  #checkov:skip=CKV_AWS_150:Deletion protection disabled in dev
  #checkov:skip=CKV_AWS_91:Access logging deferred to production
  ...
}
```

---


# 1. Terraform Formatting

## Entire repository

```bash
terraform fmt -recursive
```

## Check only (CI/CD style)

```bash
terraform fmt -recursive -check
```

Run from:

```text
vpc-aws-terraform-infra/
```

---

# 2. Terraform Validation

Validate a specific environment.

Example:

```bash
# Must run from an environment directory — not repo root
# Because Terraform needs module references resolved
cd resources/shared/dev
terraform init
terraform validate

cd resources/dashboard/dev
terraform init
terraform validate

cd resources/portfolio/dev
terraform init
terraform validate

cd resources/school/dev
terraform init
terraform validate
```

**Expected result:** `Success! The configuration is valid.`

because Terraform needs the module references resolved.

---

# 3. TFLint

**Scans:** Terraform code quality, syntax issues, deprecated arguments, provider-specific best practices, and infrastructure design issues.

## Scan current Terraform project

```bash
tflint
```

## Scan recursively

```bash
tflint --recursive
```

Run from:

```text
vpc-aws-terraform-infra/
```

or

```text
resources/shared/dev/
```

depending on what you're validating.

---

# 4. Checkov

**Scans:** Terraform, CloudFormation, Kubernetes manifests, Dockerfiles, and Infrastructure-as-Code configurations for security, compliance, and cloud best-practice violations.

## Entire repository

```bash
python -m checkov.main -d .
```

## Specific environment

```bash
python -m checkov.main -d resources/shared/dev

# Quiet output — only show failures
python -m checkov.main -d resources/portfolio/dev \
  --framework terraform --quiet


## Compact output

python -m checkov.main -d . --compact
```

## Save report

```bash
python -m checkov.main -d . -o cli > checkov-report.txt
```

Run from:

```text
vpc-aws-terraform-infra/
```

---

# 5. tfsec

**Scans:** Terraform code for AWS, Azure, and GCP security misconfigurations.

## Entire repository

```bash
tfsec .
```

## Specific environment

```bash
tfsec resources/shared/dev
```

## Save report

```bash
tfsec . > tfsec-report.txt
```

Run from:

```text
vpc-aws-terraform-infra/
```

---

# 6. Trivy has three scanning modes used in this project.

## 6a. Trivy (Terraform/IaC)

**Scans:** Terraform, Kubernetes manifests, Dockerfiles, docker-compose files, and Infrastructure-as-Code configurations.

## Scan Terraform configuration

```bash
trivy config .
```

## Scan specific environment

```bash
trivy config resources/shared/dev
```

## High severity only

```bash
trivy config --severity HIGH,CRITICAL .
```

---

## 6b.  Trivy Filesystem (Dependency Scanning)

**Scans:** Source code, local dependencies, secrets, licenses, and project files before containerization.

```bash
trivy fs .
```

---

## 6c. Trivy Container Image

**Scans:** Docker images for operating system vulnerabilities, dependency vulnerabilities, and supply-chain risks.

Recommended:

```bash
# Standard scan — uses .trivyignore automatically
trivy image \
  --severity HIGH,CRITICAL \
  --ignorefile .trivyignore \
  mecandjeo-portfolio:latest

# Skip DB update if recently updated
trivy image \
  --severity HIGH,CRITICAL \
  --ignorefile .trivyignore \
  --skip-db-update \
  mecandjeo-portfolio:latest

# Skip version check notification
trivy image \
  --severity HIGH,CRITICAL \
  --ignorefile .trivyignore \
  --skip-version-check \
  mecandjeo-portfolio:latest

# Scan ECR image directly
trivy image \
  --severity HIGH,CRITICAL \
  --ignorefile .trivyignore \
  776735193826.dkr.ecr.us-east-1.amazonaws.com/mecandjeo-infra-portfolio:latest
```

**Run from:** `vpc-aws-terraform-infra/`


---

# 7. Gitleaks

**Scans:** Git repositories, source code, commit history, configuration files, and environment files for secrets, credentials, tokens, API keys, and passwords.

## Scan current repository

```bash
gitleaks detect
```

## Scan current/source directory

```bash
gitleaks detect --source .
```

## Save report

```bash
gitleaks detect --source . --report-path gitleaks-report.json
```

Run from:

```text
vpc-aws-terraform-infra/
```

---

# 8. Safety (Python Dependencies)

**Scans:** Python dependencies against known vulnerabilities from the Safety vulnerability database.

## Scan current project

For Python projects:

```bash
cd school-platform
```

Run:

```bash
python -m safety scan
```

or


## Scan requirements file

```bash
python -m safety scan -r requirements.txt
```

Run from:

```text
school-platform/
```
**Run from:** `vpc-aws-terraform-infra/`

**Expected result for this repo:**
```
✅ apps\mecandjeo-portfolio\requirements.txt: No issues found.
✅ apps\mecandjeo-dashboard\requirements.txt: No issues found.
✅ apps\mecandjeo-school\requirements.txt: No issues found.
```

---

# 9. pip-audit

**Scans:** Installed Python packages and requirements files against public vulnerability advisories and CVE databases.

For Python projects:

## Scan installed packages

```bash
pip-audit
```

or

```bash
pip-audit -r requirements.txt
```

or

```bash
# Scan specific requirements file
python -m pip_audit \
  -r apps/mecandjeo-portfolio/requirements.txt

python -m pip_audit \
  -r apps/mecandjeo-dashboard/requirements.txt

python -m pip_audit \
  -r apps/mecandjeo-school/requirements.txt

# With ignore file — for pipeline use
python -m pip_audit \
  -r apps/mecandjeo-portfolio/requirements.txt \
  --ignore-vuln PYSEC-2026-161 \
  --ignore-vuln CVE-2025-54121 \
  --ignore-vuln CVE-2025-62727

**Run from:** `vpc-aws-terraform-infra/`
```

---

# 10. Bandit

**Scans:** Python source code for insecure coding practices such as command injection, hardcoded passwords, weak cryptography, unsafe imports, and insecure function usage.

For FastAPI/Python projects:

## Scan project

```bash
# Scan all Python files recursively
bandit -r .

# Scan specific app
bandit -r apps/mecandjeo-portfolio/

bandit -r apps/mecandjeo-dashboard/

bandit -r apps/mecandjeo-school/

# Text format output — easier to read
bandit -r apps/mecandjeo-portfolio/ -f txt

# Save report
bandit -r . -f txt > bandit-report.txt
```

**Run from:** `vpc-aws-terraform-infra/`

---

# 11. Docker Image Scanning — Full Workflow

**Scans:** Built container images for operating system vulnerabilities, package vulnerabilities, dependency vulnerabilities, and known CVEs.

The full local workflow before pushing an image to ECR:

```bash
# Step 1 — Build the image
docker build \
  --file apps/mecandjeo-portfolio/Dockerfile \
  --tag mecandjeo-portfolio:latest \
  apps/mecandjeo-portfolio/

# Step 2 — Scan with trivy
trivy image \
  --severity HIGH,CRITICAL \
  --ignorefile .trivyignore \
  mecandjeo-portfolio:latest

# Step 3 — If scan passes, push to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin \
  776735193826.dkr.ecr.us-east-1.amazonaws.com

docker tag mecandjeo-portfolio:latest \
  776735193826.dkr.ecr.us-east-1.amazonaws.com/mecandjeo-infra-portfolio:latest

docker push \
  776735193826.dkr.ecr.us-east-1.amazonaws.com/mecandjeo-infra-portfolio:latest
```

---

# Recommended Order for Terraform Repositories

### Infrastructure Repository — `vpc-aws-terraform-infra`

Run in this order — formatting first, secrets last:

```bash
# 1. Fix formatting
terraform fmt -recursive

# 2. Validate syntax per environment
cd resources/shared/dev && terraform validate && cd ../../..
cd resources/dashboard/dev && terraform validate && cd ../../..
cd resources/portfolio/dev && terraform validate && cd ../../..
cd resources/school/dev && terraform validate && cd ../../..

# 3. Lint Terraform
tflint --recursive

# 4. Scan IaC for misconfigurations
python -m checkov.main -d . --framework terraform --quiet
tfsec .
trivy config .

# 5. Scan Python dependencies
python -m safety scan
python -m pip_audit \
  -r apps/mecandjeo-portfolio/requirements.txt \
  --ignore-vuln PYSEC-2026-161 \
  --ignore-vuln CVE-2025-54121 \
  --ignore-vuln CVE-2025-62727

# 6. Scan Python source code
bandit -r apps/ -f txt

# 7. Build and scan Docker images
docker build \
  --file apps/mecandjeo-portfolio/Dockerfile \
  --tag mecandjeo-portfolio:latest \
  apps/mecandjeo-portfolio/

trivy image \
  --severity HIGH,CRITICAL \
  --ignorefile .trivyignore \
  mecandjeo-portfolio:latest

# 8. Scan for secrets
gitleaks detect --source .
```

### School Platform App — `apps/mecandjeo-school`

```bash
# From repo root
bandit -r apps/mecandjeo-school/ -f txt

python -m safety scan \
  -r apps/mecandjeo-school/requirements.txt

python -m pip_audit \
  -r apps/mecandjeo-school/requirements.txt

trivy config apps/mecandjeo-school/

docker build \
  --file apps/mecandjeo-school/Dockerfile \
  --tag mecandjeo-school:latest \
  apps/mecandjeo-school/

trivy image \
  --severity HIGH,CRITICAL \
  --ignorefile .trivyignore \
  mecandjeo-school:latest

gitleaks detect --source .
```


This order goes from:

1. Formatting
2. Syntax validation
3. Linting
4. Security scanning
5. Secret detection

---

# Quick Tool Purpose Reference

| Tool                 | What It Scans                                      | Primary Purpose                   |
| -------------------- | -------------------------------------------------- | --------------------------------- |
| `terraform fmt`      | Terraform code formatting                          | Code consistency                  |
| `terraform validate` | Terraform syntax and configuration                 | Validation                        |
| `tflint`             | Terraform code quality and best practices          | Linting                           |
| `checkov`            | Terraform, Kubernetes, Dockerfiles, CloudFormation | Security & compliance             |
| `tfsec`              | Terraform infrastructure                           | Terraform security                |
| `trivy config`       | Terraform, Dockerfiles, Kubernetes manifests       | IaC security scanning             |
| `trivy fs`           | Filesystem, dependencies, secrets                  | Dependency & secret scanning      |
| `trivy image `       | Docker/container images                            | Container security                |
| `gitleaks`           | Source code and Git history                        | Secret detection                  |
| `safety`             | Python dependencies                                | Dependency vulnerability scanning |
| `pip-audit`          | Python dependencies                                | CVE auditing                      |
| `bandit`             | Python source code                                 | Secure coding analysis            |

---



# Recommended Order for FastAPI Projects

For your school platform:

```bash
bandit -r .

python -m safety scan

pip-audit

trivy config .

gitleaks detect --source .
```

Then build and scan the container:

```bash
docker build -t school-platform .

trivy image school-platform
```

---

## Your Two Main Repositories

### Infrastructure Repository

```text
vpc-aws-terraform-infra
```

Primary tools:

* terraform fmt
* terraform validate
* tflint
* checkov
* tfsec
* trivy config
* gitleaks

### School Platform Repository

```text
school-platform
```

Primary tools:

* bandit
* safety
* pip-audit
* trivy config
* trivy image
* gitleaks

This workflow will cover most of the checks you'd typically run locally before pushing code or opening a PR.


## Phase 1 Security Gates — Pipeline Implementation

These tools are integrated into the GitHub Actions pipelines
as a `security-scan` job that runs after `validate` and
before `docker` build. If any HIGH or CRITICAL finding
is detected the pipeline stops — nothing gets deployed.

```
Pipeline flow after Phase 1:
  validate → security-scan → docker → deploy-dev → deploy-prod
                 │
                 ├── bandit     (Python source code)
                 ├── safety     (Python dependencies)
                 ├── pip-audit  (Python CVE audit)
                 ├── trivy      (Docker image after build)
                 └── checkov    (Terraform IaC)
```

See `.github/workflows/portfolio-cicd.yml` for the
full implementation of the security-scan job.

---

## Current Security Posture — This Repository

| Area                 | Status       | Notes                                                  |
|----------------------|--------------|--------------------------------------------------------|
| Python source code   | ✅ Clean    | bandit finds no issues                                 |
| Python dependencies  | ✅ Clean    | jinja2 and python-multipart upgraded                   |
| Starlette CVEs       | ✅ Accepted | Documented in `.pip-audit-ignore` — no attack surface  |
| Docker OS packages   | ✅ Clean    | apt-get upgrade in Dockerfile — libcap2 fixed          |
| perl/ncurses OS CVEs | ✅ Accepted | No Debian fix available — documented in `.trivyignore` |
| Terraform IaC        | ✅ Clean    | 0 checkov failures — 9 intentional suppressions        |
| ALB headers          | ✅ Fixed    | `drop_invalid_header_fields = true` added              |
| CloudWatch retention | ✅ Fixed    | Changed from 7 days to 365 days                        |

---

*MecanjeoOps Infrastructure — DevSecOps Reference*
*Mecandjeo Technology — Platform Engineering — 2026*
```
