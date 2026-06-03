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

Example:

```bash
cd ~/Documents/MY-DEVOPS-WORKS/PROJECTS/vpc-aws-terraform-infra
```

or

```powershell
cd C:\Users\Home\Documents\MY-DEVOPS-WORKS\PROJECTS\vpc-aws-terraform-infra
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
cd resources/shared/dev

terraform init
terraform validate
```

Run from:

```text
resources/shared/dev
```

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
```

## Compact output

```bash
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

# 6. Trivy (Terraform/IaC)

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

## Trivy Filesystem

**Scans:** Source code, local dependencies, secrets, licenses, and project files before containerization.

```bash
trivy fs .
```

---

## Trivy Container Image

**Scans:** Docker images for operating system vulnerabilities, dependency vulnerabilities, and supply-chain risks.

Recommended:

```bash
trivy image \
  --scanners vuln \
  --severity HIGH,CRITICAL \
  --ignore-unfixed \
  <image-name>
```

Example:

```bash
trivy image \
  --scanners vuln \
  --severity HIGH,CRITICAL \
  --ignore-unfixed \
  mecandjeo-portfolio:latest
```

Run from:

```text
vpc-aws-terraform-infra/
```

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
python -m pip_audit
```

## Scan requirements file

```bash
python -m pip_audit -r requirements.txt
```

Run from:

```text
school-platform/
```

---

# 10. Bandit

**Scans:** Python source code for insecure coding practices such as command injection, hardcoded passwords, weak cryptography, unsafe imports, and insecure function usage.

For FastAPI/Python projects:

## Scan project

```bash
bandit -r .
```

## Scan application folder

```bash
bandit -r app
```


Run from:

```text
school-platform/
```

---

# 11. Docker Image Scanning

**Scans:** Built container images for operating system vulnerabilities, package vulnerabilities, dependency vulnerabilities, and known CVEs.

After building an image:

```bash
docker build -t school-platform .
```

```bash
docker images
```

Example:

```bash
trivy image school-platform:latest
```

or

```bash
trivy image 776735193826.dkr.ecr.us-east-1.amazonaws.com/mecandjeo-school-platform-dev:v1.0.0
```
or

Run:

```bash
trivy image \
  --scanners vuln \
  --severity HIGH,CRITICAL \
  --ignore-unfixed \
  school-platform
```
---

# Recommended Order for Terraform Repositories

For repositories like **vpc-aws-terraform-infra**:

```bash
terraform fmt -recursive

terraform validate

tflint --recursive

python -m checkov.main -d .

tfsec .

trivy config .

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

| Tool               | What It Scans                                      | Primary Purpose                   |
| ------------------ | -------------------------------------------------- | --------------------------------- |
| terraform fmt      | Terraform code formatting                          | Code consistency                  |
| terraform validate | Terraform syntax and configuration                 | Validation                        |
| tflint             | Terraform code quality and best practices          | Linting                           |
| checkov            | Terraform, Kubernetes, Dockerfiles, CloudFormation | Security & compliance             |
| tfsec              | Terraform infrastructure                           | Terraform security                |
| trivy config       | Terraform, Dockerfiles, Kubernetes manifests       | IaC security scanning             |
| trivy fs           | Filesystem, dependencies, secrets                  | Dependency & secret scanning      |
| trivy image        | Docker/container images                            | Container security                |
| gitleaks           | Source code and Git history                        | Secret detection                  |
| safety             | Python dependencies                                | Dependency vulnerability scanning |
| pip-audit          | Python dependencies                                | CVE auditing                      |
| bandit             | Python source code                                 | Secure coding analysis            |

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
