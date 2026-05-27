# ─────────────────────────────────────────────────────────────
# MecanjeoOps Personal Portfolio
# Michael Emmanuel — Platform / DevOps Engineer
# ─────────────────────────────────────────────────────────────

import os
from datetime import datetime, timezone
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# ── App Initialization ────────────────────────────────────────
app = FastAPI(
    title="MecanjeoOps Portfolio",
    description="Personal Portfolio — Platform/DevOps Engineer",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Environment Config ────────────────────────────────────────
ENVIRONMENT = os.getenv("ENVIRONMENT", "dev")
APP_VERSION  = os.getenv("APP_VERSION",  "1.0.0")

# ─────────────────────────────────────────────────────────────
# PORTFOLIO DATA
# ─────────────────────────────────────────────────────────────

PROFILE = {
    "name":     "Michael Emmanuel",
    "role":     "Platform / DevOps Engineer",
    "tagline":  "Building production-grade infrastructure with AWS · Terraform · Docker",
    "location": "Lagos, Nigeria",
    "email":    "myke7104@gmail.com",
    "phone":    "+234-703-100-5238",
    "github":   "https://github.com/s8mike",
    "linkedin": "https://linkedin.com/in/yourprofile",
    "bio":      (
        "Results-driven Platform/DevOps Engineer with 3+ years of experience "
        "designing and deploying production-grade cloud infrastructure, automation "
        "tooling, and CI/CD pipelines. Currently a Platform Engineering Intern at "
        "Webforx Technology, recognised as Best Intern by the POC Committee for "
        "outstanding performance, collaboration, and initiative. Hands-on experience "
        "with AWS, Terraform, Kubernetes, Docker, ArgoCD, and Prometheus. Passionate "
        "about Infrastructure as Code, developer experience, and building scalable, "
        "reliable internal platforms."
    ),
    "available": True
}

SKILLS = [
    # Cloud
    {"name": "AWS",              "category": "Cloud",      "level": 75},
    {"name": "ECS Fargate",      "category": "Cloud",      "level": 75},
    {"name": "VPC / Networking", "category": "Cloud",      "level": 75},
    {"name": "EC2",              "category": "Cloud",      "level": 70},
    {"name": "S3",               "category": "Cloud",      "level": 75},
    {"name": "IAM",              "category": "Cloud",      "level": 70},
    {"name": "Lambda",           "category": "Cloud",      "level": 65},
    {"name": "CloudWatch",       "category": "Cloud",      "level": 65},
    {"name": "KMS",              "category": "Cloud",      "level": 60},
    # IaC
    {"name": "Terraform",        "category": "IaC",        "level": 80},
    {"name": "Ansible",          "category": "IaC",        "level": 65},
    {"name": "Vault",            "category": "IaC",        "level": 60},
    # Containers
    {"name": "Docker",           "category": "Containers", "level": 78},
    {"name": "Kubernetes",       "category": "Containers", "level": 55},
    {"name": "Helm",             "category": "Containers", "level": 60},
    {"name": "ArgoCD",           "category": "Containers", "level": 60},
    {"name": "Kustomize",        "category": "Containers", "level": 58},
    # CI/CD
    {"name": "GitHub Actions",   "category": "CI/CD",      "level": 75},
    {"name": "Forgejo Actions",  "category": "CI/CD",      "level": 70},
    {"name": "Jenkins",          "category": "CI/CD",      "level": 60},
    # Monitoring
    {"name": "Prometheus",       "category": "Monitoring", "level": 65},
    {"name": "Grafana",          "category": "Monitoring", "level": 65},
    {"name": "Alertmanager",     "category": "Monitoring", "level": 60},
    {"name": "Uptime Kuma",      "category": "Monitoring", "level": 60},
    # Languages
    {"name": "Python",           "category": "Languages",  "level": 65},
    {"name": "Bash / Shell",     "category": "Languages",  "level": 70},
    {"name": "YAML",             "category": "Languages",  "level": 80},
    # Tools
    {"name": "Git",              "category": "Tools",      "level": 75},
    {"name": "Linux",            "category": "Tools",      "level": 70},
    {"name": "Forgejo",          "category": "Tools",      "level": 65},
]

EXPERIENCE = [
    {
        "role":    "Platform Engineering Intern",
        "company": "Webforx Technology",
        "location": "Lagos, Nigeria",
        "period":  "March 2024 — Present",
        "achievements": [
            (
                "Built production-grade multi-application AWS infrastructure "
                "using Terraform monorepo pattern with shared infrastructure "
                "separation — three applications with independent CI/CD pipelines "
                "and isolated Terraform state files."
            ),
            (
                "Designed and implemented Terraform-managed AWS Lambda functions "
                "to detect and clean up unused resources — EBS volumes, idle ALBs, "
                "orphaned Elastic IPs, and stale CloudWatch logs — with multi-channel "
                "notifications via Mattermost and AWS SNS."
            ),
            (
                "Developed Terraform-managed AWS Lambda for EC2 start/stop "
                "automation based on instance tags, improving cost management "
                "with CloudWatch Logs for auditing."
            ),
            (
                "Implemented Terraform-managed AWS KMS keys for EBS, S3, SSM "
                "Session Manager, and Auto Scaling with automated key rotation "
                "and Lambda-based rotation with DynamoDB logging."
            ),
            (
                "Deployed Reloader using Helm and Kustomize under ArgoCD "
                "platform-tools. Configured namespace-restricted RBAC with "
                "automated sync, prune, and self-healing to prevent drift."
            ),
            (
                "Integrated Alertmanager into Grafana dashboards providing live "
                "visibility of alerts, severities, and firing/resolved status. "
                "Configured Mattermost notifications for real-time incident response."
            ),
            (
                "Refactored laravel_check.sh to dynamically validate Laravel "
                "backend environment variables and integrated into CI/CD pipelines "
                "for automated environment verification."
            ),
        ],
        "award": "Best Intern Award — Webforx POC Committee",
        "tags":  [
            "AWS", "Terraform", "Lambda", "KMS", "Docker",
            "GitHub Actions", "ArgoCD", "Helm", "Prometheus",
            "Grafana", "Alertmanager", "Python", "Bash"
        ]
    },
    {
        "role":    "DevOps Engineer",
        "company": "EK Tech Software Solutions",
        "location": "Texas, USA (Remote)",
        "period":  "May 2021 — January 2024",
        "achievements": [
            (
                "Automated AWS infrastructure deployments using Terraform and "
                "Ansible, reducing provisioning time by 70%."
            ),
            (
                "Designed multi-account AWS networking strategy using Transit "
                "Gateway and VPC peering for secure cross-account communication."
            ),
            (
                "Developed CI/CD pipelines using Jenkins, GitHub Actions, and "
                "ArgoCD, improving software release efficiency by 50%."
            ),
            (
                "Managed Kubernetes cluster architectures, deploying "
                "mission-critical applications with Helm and Terraform."
            ),
            (
                "Implemented AWS IAM best practices, reducing security "
                "incidents by 50%."
            ),
            (
                "Designed AWS ECS clusters with ALB and auto scaling, "
                "improving application resilience."
            ),
            (
                "Implemented Python scripts in CI/CD pipelines to extract "
                "application secrets from vaults and supply them securely "
                "as system variables."
            ),
            (
                "Developed Ansible playbooks for automated patching and "
                "configuration management across AWS and on-prem systems."
            ),
            (
                "Monitored cloud infrastructure using Prometheus, Grafana, "
                "and AWS CloudWatch, ensuring system stability."
            ),
        ],
        "award": "",
        "tags":  [
            "AWS", "Terraform", "Ansible", "Kubernetes", "Helm",
            "Jenkins", "GitHub Actions", "ArgoCD", "Python",
            "Prometheus", "Grafana", "CloudWatch"
        ]
    },
]

PROJECTS = [
    {
        "title":       "AWS Multi-App Platform Infrastructure",
        "subtitle":    "Production-grade IaC with Terraform monorepo",
        "description": (
            "Designed and provisioned a complete multi-application AWS "
            "infrastructure using Terraform monorepo pattern with shared "
            "infrastructure separation. Three applications deployed "
            "simultaneously with independent CI/CD pipelines and isolated "
            "Terraform state files. ECS Fargate, ALB, auto scaling, and "
            "S3 remote state with namespaced keys."
        ),
        "tags":      ["Terraform", "AWS", "ECS", "Docker", "GitHub Actions", "Python"],
        "github":    "https://github.com/s8mike/aws-terraform-infra",
        "live":      "",
        "highlight": True
    },
    {
        "title":       "MecanjeoOps Dashboard",
        "subtitle":    "Live DevOps status dashboard",
        "description": (
            "Real-time DevOps operations dashboard built with Python FastAPI "
            "and vanilla JavaScript. Displays live system metrics, infrastructure "
            "status, service health indicators, and deployment history timeline. "
            "Containerised with Docker multi-stage build and deployed on AWS ECS "
            "Fargate with auto scaling and Application Load Balancer."
        ),
        "tags":      ["Python", "FastAPI", "Docker", "AWS ECS", "ALB", "JavaScript"],
        "github":    "https://github.com/s8mike/aws-terraform-infra",
        "live":      "",
        "highlight": True
    },
    {
        "title":       "AWS Resource Automation",
        "subtitle":    "Lambda-based unused resource cleanup — Webforx Technology",
        "description": (
            "Terraform-managed AWS Lambda functions to detect and automatically "
            "clean up unused AWS resources — EBS volumes, idle load balancers, "
            "orphaned Elastic IPs, and stale CloudWatch logs. Multi-channel "
            "notifications via Mattermost and AWS SNS. All resources fully "
            "IaC-managed with Terraform."
        ),
        "tags":      ["AWS Lambda", "Terraform", "SNS", "Mattermost", "Python"],
        "github":    "",
        "live":      "",
        "highlight": True
    },
    {
        "title":       "Kubernetes GitOps Deployment",
        "subtitle":    "ArgoCD · Helm · Kustomize — Webforx Technology",
        "description": (
            "Deployed Reloader using Helm and Kustomize under ArgoCD "
            "platform-tools project. Automated pod reloads when ConfigMaps "
            "or Secrets are updated. Configured namespace-restricted RBAC "
            "with automated sync, prune, and self-healing to prevent drift."
        ),
        "tags":      ["Kubernetes", "ArgoCD", "Helm", "Kustomize", "GitOps", "RBAC"],
        "github":    "",
        "live":      "",
        "highlight": False
    },
    {
        "title":       "Multi-App CI/CD Pipeline Automation",
        "subtitle":    "GitHub Actions — independent parallel pipelines",
        "description": (
            "Three independent GitHub Actions pipelines for shared infrastructure, "
            "dashboard, and portfolio applications. Each pipeline validates Terraform "
            "code, builds Docker images, pushes to Docker Hub and AWS ECR, and "
            "deploys to ECS Fargate automatically. Manual approval gate for production."
        ),
        "tags":      ["GitHub Actions", "Docker", "ECR", "Terraform", "CI/CD"],
        "github":    "https://github.com/s8mike/aws-terraform-infra",
        "live":      "",
        "highlight": False
    },
    {
        "title":       "Monitoring Stack",
        "subtitle":    "Prometheus · Grafana · Alertmanager — Webforx Technology",
        "description": (
            "Complete observability stack with Prometheus for metrics collection, "
            "Grafana for visualisation and dashboards, and Alertmanager for alert "
            "routing. Configured Mattermost notifications for real-time incident "
            "response. Custom alerting rules for infrastructure and application "
            "monitoring."
        ),
        "tags":      ["Prometheus", "Grafana", "Alertmanager", "Mattermost", "DevOps"],
        "github":    "",
        "live":      "",
        "highlight": False
    },
    {
        "title":       "School Management Platform",
        "subtitle":    "FastAPI + PostgreSQL + JWT Authentication",
        "description": (
            "RESTful API for school management with JWT authentication, "
            "role-based access control, and full CRUD operations for "
            "student and course management. Containerised with Docker "
            "and integrated into the shared AWS infrastructure monorepo."
        ),
        "tags":      ["Python", "FastAPI", "PostgreSQL", "SQLAlchemy", "JWT", "Docker"],
        "github":    "https://github.com/s8mike/mecandjeo-school-platform",
        "live":      "",
        "highlight": False
    },
]

# ─────────────────────────────────────────────────────────────
# API ROUTES
# ─────────────────────────────────────────────────────────────

@app.get("/health", tags=["Health"])
async def health_check():
    return JSONResponse(
        status_code=200,
        content={
            "status":      "healthy",
            "timestamp":   datetime.now(timezone.utc).isoformat(),
            "environment": ENVIRONMENT,
            "version":     APP_VERSION,
        }
    )


@app.get("/api/profile", tags=["Portfolio"])
async def get_profile():
    return {
        **PROFILE,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@app.get("/api/skills", tags=["Portfolio"])
async def get_skills():
    categories = list(dict.fromkeys(s["category"] for s in SKILLS))
    grouped = {
        cat: [s for s in SKILLS if s["category"] == cat]
        for cat in categories
    }
    return {
        "skills":     SKILLS,
        "grouped":    grouped,
        "categories": categories,
        "total":      len(SKILLS),
        "timestamp":  datetime.now(timezone.utc).isoformat()
    }


@app.get("/api/projects", tags=["Portfolio"])
async def get_projects():
    return {
        "projects":  PROJECTS,
        "total":     len(PROJECTS),
        "highlight": [p for p in PROJECTS if p["highlight"]],
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@app.get("/api/experience", tags=["Portfolio"])
async def get_experience():
    return {
        "experience": EXPERIENCE,
        "total":      len(EXPERIENCE),
        "timestamp":  datetime.now(timezone.utc).isoformat()
    }


# ── Serve Frontend ────────────────────────────────────────────
app.mount(
    "/",
    StaticFiles(directory="static", html=True),
    name="static"
)