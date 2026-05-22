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
        "Platform engineering intern with Webforx Technology with hands-on experience designing "
        "and deploying production-grade AWS infrastructure using Terraform "
        "and Docker. Passionate about Infrastructure as Code, CI/CD automation, "
        "and building scalable, reliable systems."
    ),
    "available": True
}

SKILLS = [
    # Cloud
    { "name": "AWS",           "category": "Cloud",     "level": 85 },
    { "name": "ECS Fargate",   "category": "Cloud",     "level": 80 },
    { "name": "VPC / Networking", "category": "Cloud",  "level": 80 },
    { "name": "EC2",           "category": "Cloud",     "level": 75 },
    { "name": "S3",            "category": "Cloud",     "level": 80 },
    { "name": "IAM",           "category": "Cloud",     "level": 75 },
    { "name": "CloudWatch",    "category": "Cloud",     "level": 70 },
    # IaC
    { "name": "Terraform",     "category": "IaC",       "level": 85 },
    { "name": "Docker",        "category": "Containers","level": 80 },
    { "name": "Kubernetes",    "category": "Containers","level": 65 },
    # CI/CD
    { "name": "GitHub Actions","category": "CI/CD",     "level": 80 },
    { "name": "CI/CD Pipelines","category": "CI/CD",    "level": 75 },
    # Languages
    { "name": "Python",        "category": "Languages",  "level": 70 },
    { "name": "Bash / Shell",  "category": "Languages",  "level": 75 },
    { "name": "YAML",          "category": "Languages",  "level": 85 },
    # Tools
    { "name": "Git",           "category": "Tools",      "level": 80 },
    { "name": "Linux",         "category": "Tools",      "level": 75 },
]

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