# ─────────────────────────────────────────────────────────────
# MecandjeoOps Personal Portfolio
# Platform / DevOps Engineer
# ─────────────────────────────────────────────────────────────

import os
from datetime import datetime, timezone
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# ── App Initialization ────────────────────────────────────────
app = FastAPI(
    title="MecandjeoOps Portfolio",
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
ENVIRONMENT  = os.getenv("ENVIRONMENT",  "dev")
APP_VERSION  = os.getenv("APP_VERSION",  "1.0.0")

# ─────────────────────────────────────────────────────────────
# PORTFOLIO DATA
# Update these sections with real information
# then push to trigger automatic redeployment
# ─────────────────────────────────────────────────────────────

PROFILE = {
    "name":     "Michael Emmanuel",
    "role":     "Platform / DevOps Engineer",
    "tagline":  "Building production-grade infrastructure with AWS · Terraform · Docker",
    "location": "Lagos, Nigeria",
    "email":    "myke7104@gmail.com",
    "github":   "https://github.com/s8mike",
    "linkedin": "https://linkedin.com/in/yourprofile",
    "bio":      (
        "Platform engineering intern at Webforx Technology with hands-on experience "
        "designing and deploying production-grade AWS infrastructure using Terraform "
        "and Docker. Built monitoring solutions with Prometheus, Grafana, and Alertmanager, "
        "developed DevOps automation tools using Bash and Python, and created repository "
        "management utilities integrating with Forgejo. Passionate about Infrastructure as Code, "
        "CI/CD automation, and building scalable, reliable systems."
    ),
    "available": True
}
SKILLS = [
    # Cloud
    { "name": "AWS",           "category": "Cloud",     "level": 85 },
    { "name": "Lambda",        "category": "Cloud",     "level": 75 },
    { "name": "ECS Fargate",   "category": "Cloud",     "level": 80 },
    { "name": "VPC / Networking", "category": "Cloud",  "level": 80 },
    { "name": "EC2",           "category": "Cloud",     "level": 80 },
    { "name": "S3",            "category": "Cloud",     "level": 80 },
    { "name": "IAM",           "category": "Cloud",     "level": 75 },
    { "name": "CloudWatch",    "category": "Cloud",     "level": 75 },
    # IaC
    { "name": "Terraform",     "category": "IaC",       "level": 85 },
    { "name": "Docker",        "category": "Containers","level": 80 },
    { "name": "Kubernetes",    "category": "Containers","level": 65 },
    # Monitoring
    { "name": "Prometheus",    "category": "Monitoring","level": 75 },
    { "name": "Grafana",       "category": "Monitoring","level": 75 },
    { "name": "Alertmanager",  "category": "Monitoring","level": 70 },
    # CI/CD
    { "name": "GitHub Actions","category": "CI/CD",     "level": 80 },
    { "name": "CI/CD Pipelines","category": "CI/CD",    "level": 75 },
    # Languages
    { "name": "Python",        "category": "Languages",  "level": 75 },
    { "name": "Flask",         "category": "Languages",  "level": 70 },
    { "name": "Bash / Shell",  "category": "Languages",  "level": 80 },
    { "name": "YAML",          "category": "Languages",  "level": 85 },
    # Tools
    { "name": "Git",           "category": "Tools",      "level": 80 },
    { "name": "Forgejo",       "category": "Tools",      "level": 70 },
    { "name": "Linux",         "category": "Tools",      "level": 75 },
    { "name": "jq",            "category": "Tools",      "level": 75 },
    { "name": "curl",          "category": "Tools",      "level": 75 },
    { "name": "Mattermost",    "category": "Tools",      "level": 70 },
];


# SKILLS = [
#     # Cloud
#     { "name": "AWS",           "category": "Cloud",     "level": 85 },
#     { "name": "ECS Fargate",   "category": "Cloud",     "level": 80 },
#     { "name": "VPC / Networking", "category": "Cloud",  "level": 80 },
#     { "name": "EC2",           "category": "Cloud",     "level": 75 },
#     { "name": "S3",            "category": "Cloud",     "level": 80 },
#     { "name": "IAM",           "category": "Cloud",     "level": 75 },
#     { "name": "CloudWatch",    "category": "Cloud",     "level": 70 },
#     # IaC
#     { "name": "Terraform",     "category": "IaC",       "level": 85 },
#     { "name": "Docker",        "category": "Containers","level": 80 },
#     { "name": "Kubernetes",    "category": "Containers","level": 65 },
#     # CI/CD
#     { "name": "GitHub Actions","category": "CI/CD",     "level": 80 },
#     { "name": "CI/CD Pipelines","category": "CI/CD",    "level": 75 },
#     # Languages
#     { "name": "Python",        "category": "Languages",  "level": 70 },
#     { "name": "Bash / Shell",  "category": "Languages",  "level": 75 },
#     { "name": "YAML",          "category": "Languages",  "level": 85 },
#     # Tools
#     { "name": "Git",           "category": "Tools",      "level": 80 },
#     { "name": "Linux",         "category": "Tools",      "level": 75 },
# ]

PROJECTS = [
    {
        "title":       "AWS Auto-Scaling Infrastructure",
        "subtitle":    "Production-grade IaC with Terraform",
        "description": (
            "Designed and provisioned a complete AWS infrastructure using "
            "Terraform monorepo pattern. Includes custom VPC, ECS Fargate, "
            "Application Load Balancer, auto scaling, and remote S3 state "
            "management. Deployed a real FastAPI application with a full "
            "GitHub Actions CI/CD pipeline."
        ),
        "tags":   ["Terraform", "AWS", "ECS", "Docker", "GitHub Actions", "Python"],
        "github": "https://github.com/s8mike/aws-terraform-infra",
        "live":   "",
        "highlight": True
    },
    {
        "title":       "MecandjeoOps Dashboard",
        "subtitle":    "Live DevOps status dashboard",
        "description": (
            "Real-time DevOps dashboard built with Python FastAPI and "
            "vanilla JavaScript. Displays live system metrics, infrastructure "
            "status, service health, and deployment history. Containerised "
            "with Docker and deployed on AWS ECS Fargate."
        ),
        "tags":   ["Python", "FastAPI", "Docker", "AWS ECS", "ALB"],
        "github": "https://github.com/s8mike/aws-terraform-infra",
        "live":   "",
        "highlight": True
    },
    {
        "title":       "CI/CD Pipeline Automation",
        "subtitle":    "GitHub Actions — Build, push, deploy",
        "description": (
            "Full CI/CD pipeline using GitHub Actions that validates "
            "Terraform code, builds Docker images, pushes to both Docker Hub "
            "and AWS ECR, and deploys to ECS Fargate automatically on every "
            "push to main. Manual approval gate for production deployments."
        ),
        "tags":   ["GitHub Actions", "Docker", "ECR", "Terraform", "CI/CD"],
        "github": "https://github.com/s8mike/aws-terraform-infra",
        "live":   "",
        "highlight": False
    }, 
    {
        "title":       "Prometheus-Grafana-Mattermost Monitoring Stack",
        "subtitle":    "Containerized monitoring & alerting infrastructure",
        "description": "Built and deployed a complete monitoring stack integrating Prometheus for metrics collection, Alertmanager for alert routing, and Grafana for visualization. Developed a custom Python Flask webhook converter to translate Alertmanager webhooks into Mattermost-compatible format, enabling real-time team notifications. Containerized all services using Docker with internal networking, persistent storage, and automated health checks.",
        "tags":        ["Prometheus", "Grafana", "Alertmanager", "Python", "Flask", "Docker", "Mattermost", "Monitoring", "DevOps"],
        "github":      "https://github.com/s8mike/Alertmanager-grafana",
        "live":        "",
        "highlight":   True
    },
    {
        "title":       "repo-sync-tools",
        "subtitle":    "Forgejo repository synchronization & PR visibility tool",
        "description": "Built a DevOps automation tool for synchronizing repositories from a Forgejo organization to local environments. Implemented automatic repo cloning/pulling, open pull request scanning, and stale PR detection with age calculation. Designed as an idempotent Bash script with fail-fast error handling using 'set -euo pipefail' for reliable repeated execution.",
        "tags":        ["Bash", "Forgejo", "Git", "API Integration", "DevOps", "Automation", "jq", "curl"],
        "github":      "https://github.com/s8mike/repo-sync-tools",
        "live":        "",
        "highlight":   True
    },
    {
        "title":       "DevOps Tools Scanner",
        "subtitle":    "Bash script for automated DevOps tool detection & reporting",
        "description": "Developed a cross-platform Bash script that automatically scans systems to detect and catalog installed DevOps tools (Kubernetes, Docker, IaC, Cloud CLI, etc.). Implements smart categorization, size calculation, CSV export with timestamps, and color-coded terminal output. Supports Windows (MINGW64), Linux, and macOS with optional Docker image/container scanning and VS Code extension listing.",
        "tags":        ["Bash", "DevOps", "Automation", "Scripting", "System Administration", "CSV", "Reporting"],
        "github":      "",
        "live":        "",
        "highlight":   True
    },
    {
        "title":       "EC2 Scheduler Lambda Module",
        "subtitle":    "Terraform module for scheduled EC2 instance start/stop",
        "description": "Developed a Terraform module that provisions a Lambda function to automatically start or stop EC2 instances on a schedule for cost optimization. Implemented tag-based instance filtering via environment variables, built-in Mattermost webhook notifications with retry logic, and CloudWatch Logs integration. The Lambda handler filters instances by tag key/value and sends formatted notifications with tracking IDs after each operation.",
        "tags":        ["AWS", "Lambda", "Terraform", "Python", "boto3", "EC2", "CloudWatch", "Mattermost", "DevOps", "IaC"],
        "github":      "",
        "live":        "",
        "highlight":   True
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


# ── Serve Frontend ────────────────────────────────────────────
app.mount(
    "/",
    StaticFiles(directory="static", html=True),
    name="static"
)