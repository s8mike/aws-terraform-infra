# ─────────────────────────────────────────────────────────────
# MecanjeoOps Personal Portfolio
# Platform / DevOps Engineer
# ─────────────────────────────────────────────────────────────

import os
import uuid
import logging
from datetime import datetime, timezone
from typing import List, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from pydantic import BaseModel, HttpUrl, EmailStr, Field
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# ── Logging Configuration ─────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(request_id)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ── Rate Limiting Setup ───────────────────────────────────────
limiter = Limiter(key_func=get_remote_address, default_limits=["200/hour"])

# ── Settings Configuration ────────────────────────────────────
class Settings(BaseModel):
    environment: str = Field(default="dev")
    app_version: str = Field(default="1.0.0")
    debug: bool = Field(default=False)
    rate_limit_enabled: bool = Field(default=True)
    cache_enabled: bool = Field(default=False)  # Set to True if Redis available
    
    class Config:
        env_file = ".env"

settings = Settings()

# ── Response Models ───────────────────────────────────────────
class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    timestamp: str
    request_id: Optional[str] = None

class ProfileResponse(BaseModel):
    name: str
    role: str
    tagline: str
    location: str
    email: str
    github: HttpUrl
    linkedin: HttpUrl
    bio: str
    available: bool
    timestamp: str

class SkillResponse(BaseModel):
    name: str
    category: str
    level: int

class SkillsResponse(BaseModel):
    skills: List[SkillResponse]
    grouped: dict
    categories: List[str]
    total: int
    timestamp: str

class ProjectResponse(BaseModel):
    title: str
    subtitle: str
    description: str
    tags: List[str]
    github: Optional[HttpUrl] = None
    live: Optional[HttpUrl] = None
    highlight: bool

class ProjectsResponse(BaseModel):
    projects: List[ProjectResponse]
    total: int
    highlight: List[ProjectResponse]
    timestamp: str

class ContactMessage(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    subject: str = Field(..., min_length=3, max_length=200)
    message: str = Field(..., min_length=10, max_length=5000)

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    environment: str
    version: str
    request_id: Optional[str] = None

# ── Portfolio Data ────────────────────────────────────────────
PROFILE = {
    "name": "Michael Emmanuel",
    "role": "Platform / DevOps Engineer",
    "tagline": "Building production-grade infrastructure with AWS · Terraform · Docker",
    "location": "Lagos, Nigeria",
    "email": "myke7104@gmail.com",
    "github": "https://github.com/s8mike",
    "linkedin": "https://linkedin.com/in/yourprofile",
    "bio": (
        "Platform engineering intern with hands-on experience designing "
        "and deploying production-grade AWS infrastructure using Terraform "
        "and Docker. Passionate about Infrastructure as Code, CI/CD automation, "
        "and building scalable, reliable systems."
    ),
    "available": True
}

SKILLS = [
    # Cloud
    {"name": "AWS", "category": "Cloud", "level": 85},
    {"name": "ECS Fargate", "category": "Cloud", "level": 80},
    {"name": "VPC / Networking", "category": "Cloud", "level": 80},
    {"name": "EC2", "category": "Cloud", "level": 75},
    {"name": "S3", "category": "Cloud", "level": 80},
    {"name": "IAM", "category": "Cloud", "level": 75},
    {"name": "CloudWatch", "category": "Cloud", "level": 70},
    # IaC
    {"name": "Terraform", "category": "IaC", "level": 85},
    {"name": "Docker", "category": "Containers", "level": 80},
    {"name": "Kubernetes", "category": "Containers", "level": 65},
    # CI/CD
    {"name": "GitHub Actions", "category": "CI/CD", "level": 80},
    {"name": "CI/CD Pipelines", "category": "CI/CD", "level": 75},
    # Languages
    {"name": "Python", "category": "Languages", "level": 70},
    {"name": "Bash / Shell", "category": "Languages", "level": 75},
    {"name": "YAML", "category": "Languages", "level": 85},
    # Tools
    {"name": "Git", "category": "Tools", "level": 80},
    {"name": "Linux", "category": "Tools", "level": 75},
]

PROJECTS = [
    {
        "title": "AWS Auto-Scaling Infrastructure",
        "subtitle": "Production-grade IaC with Terraform",
        "description": (
            "Designed and provisioned a complete AWS infrastructure using "
            "Terraform monorepo pattern. Includes custom VPC, ECS Fargate, "
            "Application Load Balancer, auto scaling, and remote S3 state "
            "management. Deployed a real FastAPI application with a full "
            "GitHub Actions CI/CD pipeline."
        ),
        "tags": ["Terraform", "AWS", "ECS", "Docker", "GitHub Actions", "Python"],
        "github": "https://github.com/s8mike/aws-terraform-infra",
        "live": "",
        "highlight": True
    },
    {
        "title": "MecanjeoOps Dashboard",
        "subtitle": "Live DevOps status dashboard",
        "description": (
            "Real-time DevOps dashboard built with Python FastAPI and "
            "vanilla JavaScript. Displays live system metrics, infrastructure "
            "status, service health, and deployment history. Containerised "
            "with Docker and deployed on AWS ECS Fargate."
        ),
        "tags": ["Python", "FastAPI", "Docker", "AWS ECS", "ALB"],
        "github": "https://github.com/s8mike/aws-terraform-infra",
        "live": "",
        "highlight": True
    },
    {
        "title": "CI/CD Pipeline Automation",
        "subtitle": "GitHub Actions — Build, push, deploy",
        "description": (
            "Full CI/CD pipeline using GitHub Actions that validates "
            "Terraform code, builds Docker images, pushes to both Docker Hub "
            "and AWS ECR, and deploys to ECS Fargate automatically on every "
            "push to main. Manual approval gate for production deployments."
        ),
        "tags": ["GitHub Actions", "Docker", "ECR", "Terraform", "CI/CD"],
        "github": "https://github.com/s8mike/aws-terraform-infra",
        "live": "",
        "highlight": False
    },
]

# ── Lifespan Management ───────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info(f"Starting {app.title} v{settings.app_version} in {settings.environment} mode")
    app.state.limiter = limiter
    yield
    # Shutdown
    logger.info(f"Shutting down {app.title}")

# ── App Initialization ────────────────────────────────────────
app = FastAPI(
    title="MecanjeoOps Portfolio",
    description="""
    ## Platform/DevOps Engineer Portfolio API
    
    This API powers my personal portfolio website with:
    
    * **Profile Information** - Bio, contact, social links
    * **Technical Skills** - Categorized with proficiency levels  
    * **Project Portfolio** - Infrastructure and DevOps projects
    
    ### Technology Stack
    - FastAPI for high-performance API
    - Static files for portfolio frontend
    - Rate limiting for abuse protection
    - CORS configured for security
    """,
    version=settings.app_version,
    docs_url="/api/docs" if settings.debug else None,
    redoc_url="/api/redoc" if settings.debug else None,
    openapi_tags=[
        {"name": "Portfolio", "description": "Portfolio data endpoints"},
        {"name": "Health", "description": "Health and readiness checks"},
        {"name": "Contact", "description": "Contact and messaging"}
    ],
    lifespan=lifespan,
    debug=settings.debug
)

# Add rate limit exception handler
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ── Middleware ────────────────────────────────────────────────
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    """Add unique request ID for tracing"""
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    
    # Add request_id to logger context
    old_factory = logging.getLogRecordFactory()
    def record_factory(*args, **kwargs):
        record = old_factory(*args, **kwargs)
        record.request_id = getattr(request.state, 'request_id', 'N/A')
        return record
    logging.setLogRecordFactory(record_factory)
    
    logger.info(f"Request started: {request.method} {request.url.path}")
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    logger.info(f"Request completed: {response.status_code}")
    return response

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Add security headers to all responses"""
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    if settings.environment == "prod":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response

# Configure CORS based on environment
if settings.environment == "prod":
    origins = [
        "https://yourdomain.com",
        "https://www.yourdomain.com",
    ]
else:
    origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID"],
)

# Add trusted host middleware in production
if settings.environment == "prod":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["yourdomain.com", "*.yourdomain.com", "api.yourdomain.com"]
    )

# ── Exception Handlers ───────────────────────────────────────
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.detail if isinstance(exc.detail, str) else "HTTP Error",
            detail=str(exc.detail),
            timestamp=datetime.now(timezone.utc).isoformat(),
            request_id=getattr(request.state, 'request_id', None)
        ).model_dump()
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal Server Error",
            detail="An unexpected error occurred" if settings.debug else None,
            timestamp=datetime.now(timezone.utc).isoformat(),
            request_id=getattr(request.state, 'request_id', None)
        ).model_dump()
    )

# ── API Routes ────────────────────────────────────────────────
@app.get("/health", response_model=HealthResponse, tags=["Health"])
@limiter.limit("10/minute")
async def health_check(request: Request):
    """Basic health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(timezone.utc).isoformat(),
        environment=settings.environment,
        version=settings.app_version,
        request_id=getattr(request.state, 'request_id', None)
    )

@app.get("/health/live", tags=["Health"])
async def liveness_probe():
    """Kubernetes liveness probe - always returns 200 if app is running"""
    return {"status": "alive", "timestamp": datetime.now(timezone.utc).isoformat()}

@app.get("/health/ready", tags=["Health"])
async def readiness_probe(request: Request):
    """Kubernetes readiness probe - checks dependencies"""
    deps_status = {
        "api": "healthy",
        "static_files": "healthy" if os.path.exists("static") else "unhealthy",
    }
    
    if any(s == "unhealthy" for s in deps_status.values()):
        return JSONResponse(
            status_code=503,
            content={
                "status": "not ready",
                "dependencies": deps_status,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "request_id": getattr(request.state, 'request_id', None)
            }
        )
    return {
        "status": "ready",
        "dependencies": deps_status,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@app.get("/api/profile", response_model=ProfileResponse, tags=["Portfolio"])
@limiter.limit("60/minute")
async def get_profile(request: Request):
    """Get personal profile information"""
    return {
        **PROFILE,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@app.get("/api/skills", response_model=SkillsResponse, tags=["Portfolio"])
@limiter.limit("60/minute")
async def get_skills(request: Request):
    """Get technical skills categorized by domain"""
    categories = list(dict.fromkeys(s["category"] for s in SKILLS))
    grouped = {
        cat: [s for s in SKILLS if s["category"] == cat]
        for cat in categories
    }
    return {
        "skills": SKILLS,
        "grouped": grouped,
        "categories": categories,
        "total": len(SKILLS),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@app.get("/api/projects", response_model=ProjectsResponse, tags=["Portfolio"])
@limiter.limit("60/minute")
async def get_projects(request: Request):
    """Get portfolio projects with optional filtering"""
    return {
        "projects": PROJECTS,
        "total": len(PROJECTS),
        "highlight": [p for p in PROJECTS if p.get("highlight", False)],
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@app.post("/api/contact", tags=["Contact"])
@limiter.limit("5/hour")
async def send_contact_message(contact: ContactMessage, request: Request):
    """
    Send a contact message.
    Rate limited to 5 messages per hour per IP.
    """
    # Log the message (in production, send to email/Slack/CRM)
    logger.info(f"Contact message from {contact.email}: {contact.subject}")
    
    # TODO: Integrate with email service (AWS SES, SendGrid, etc.)
    # Example: send_email(contact.email, contact.subject, contact.message)
    
    return {
        "message": "Message received successfully",
        "reference": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

# ── Static Files ──────────────────────────────────────────────
# Mount static files only if directory exists
if os.path.exists("static"):
    app.mount(
        "/",
        StaticFiles(directory="static", html=True),
        name="static"
    )
else:
    logger.warning("Static directory not found - frontend will not be served")

# ── Root Redirect ─────────────────────────────────────────────
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint - API information"""
    return {
        "name": "MecanjeoOps Portfolio API",
        "version": settings.app_version,
        "environment": settings.environment,
        "endpoints": {
            "docs": "/api/docs" if settings.debug else "disabled",
            "health": "/health",
            "profile": "/api/profile",
            "skills": "/api/skills",
            "projects": "/api/projects",
            "contact": "/api/contact"
        },
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

# ── Metrics Endpoint (Optional) ──────────────────────────────
@app.get("/metrics", tags=["Monitoring"])
@limiter.limit("10/minute")
async def get_metrics(request: Request):
    """Simple metrics endpoint for monitoring"""
    return {
        "uptime_seconds": (datetime.now(timezone.utc) - app.state.start_time).total_seconds() 
                          if hasattr(app.state, 'start_time') else 0,
        "requests_processed": getattr(app.state, 'request_count', 0),
        "active_connections": 0,  # Would need connection tracking
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

# Store start time for metrics
app.state.start_time = datetime.now(timezone.utc)

# Request counter middleware
@app.middleware("http")
async def count_requests(request: Request, call_next):
    if not hasattr(app.state, 'request_count'):
        app.state.request_count = 0
    app.state.request_count += 1
    return await call_next(request)

# ── Main Entry Point ──────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="info"
    )









# # ─────────────────────────────────────────────────────────────
# # MecandjeoOps Personal Portfolio
# # Platform / DevOps Engineer
# # ─────────────────────────────────────────────────────────────

# import os
# from datetime import datetime, timezone
# from fastapi import FastAPI
# from fastapi.staticfiles import StaticFiles
# from fastapi.responses import JSONResponse
# from fastapi.middleware.cors import CORSMiddleware

# # ── App Initialization ────────────────────────────────────────
# app = FastAPI(
#     title="MecandjeoOps Portfolio",
#     description="Personal Portfolio — Platform/DevOps Engineer",
#     version="1.0.0"
# )

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # ── Environment Config ────────────────────────────────────────
# ENVIRONMENT  = os.getenv("ENVIRONMENT",  "dev")
# APP_VERSION  = os.getenv("APP_VERSION",  "1.0.0")

# # ─────────────────────────────────────────────────────────────
# # PORTFOLIO DATA
# # Update these sections with real information
# # then push to trigger automatic redeployment
# # ─────────────────────────────────────────────────────────────

# PROFILE = {
#     "name":     "Michael Emmanuel",
#     "role":     "Platform / DevOps Engineer",
#     "tagline":  "Building production-grade infrastructure with AWS · Terraform · Docker",
#     "location": "Lagos, Nigeria",
#     "email":    "myke7104@gmail.com",
#     "github":   "https://github.com/s8mike",
#     "linkedin": "https://linkedin.com/in/yourprofile",
#     "bio":      (
#         "Platform engineering intern with hands-on experience designing "
#         "and deploying production-grade AWS infrastructure using Terraform "
#         "and Docker. Passionate about Infrastructure as Code, CI/CD automation, "
#         "and building scalable, reliable systems."
#     ),
#     "available": True
# }

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

# PROJECTS = [
#     {
#         "title":       "AWS Auto-Scaling Infrastructure",
#         "subtitle":    "Production-grade IaC with Terraform",
#         "description": (
#             "Designed and provisioned a complete AWS infrastructure using "
#             "Terraform monorepo pattern. Includes custom VPC, ECS Fargate, "
#             "Application Load Balancer, auto scaling, and remote S3 state "
#             "management. Deployed a real FastAPI application with a full "
#             "GitHub Actions CI/CD pipeline."
#         ),
#         "tags":   ["Terraform", "AWS", "ECS", "Docker", "GitHub Actions", "Python"],
#         "github": "https://github.com/s8mike/aws-terraform-infra",
#         "live":   "",
#         "highlight": True
#     },
#     {
#         "title":       "MecandjeoOps Dashboard",
#         "subtitle":    "Live DevOps status dashboard",
#         "description": (
#             "Real-time DevOps dashboard built with Python FastAPI and "
#             "vanilla JavaScript. Displays live system metrics, infrastructure "
#             "status, service health, and deployment history. Containerised "
#             "with Docker and deployed on AWS ECS Fargate."
#         ),
#         "tags":   ["Python", "FastAPI", "Docker", "AWS ECS", "ALB"],
#         "github": "https://github.com/s8mike/aws-terraform-infra",
#         "live":   "",
#         "highlight": True
#     },
#     {
#         "title":       "CI/CD Pipeline Automation",
#         "subtitle":    "GitHub Actions — Build, push, deploy",
#         "description": (
#             "Full CI/CD pipeline using GitHub Actions that validates "
#             "Terraform code, builds Docker images, pushes to both Docker Hub "
#             "and AWS ECR, and deploys to ECS Fargate automatically on every "
#             "push to main. Manual approval gate for production deployments."
#         ),
#         "tags":   ["GitHub Actions", "Docker", "ECR", "Terraform", "CI/CD"],
#         "github": "https://github.com/s8mike/aws-terraform-infra",
#         "live":   "",
#         "highlight": False
#     },
# ]

# # ─────────────────────────────────────────────────────────────
# # API ROUTES
# # ─────────────────────────────────────────────────────────────

# @app.get("/health", tags=["Health"])
# async def health_check():
#     return JSONResponse(
#         status_code=200,
#         content={
#             "status":      "healthy",
#             "timestamp":   datetime.now(timezone.utc).isoformat(),
#             "environment": ENVIRONMENT,
#             "version":     APP_VERSION,
#         }
#     )


# @app.get("/api/profile", tags=["Portfolio"])
# async def get_profile():
#     return {
#         **PROFILE,
#         "timestamp": datetime.now(timezone.utc).isoformat()
#     }


# @app.get("/api/skills", tags=["Portfolio"])
# async def get_skills():
#     categories = list(dict.fromkeys(s["category"] for s in SKILLS))
#     grouped = {
#         cat: [s for s in SKILLS if s["category"] == cat]
#         for cat in categories
#     }
#     return {
#         "skills":     SKILLS,
#         "grouped":    grouped,
#         "categories": categories,
#         "total":      len(SKILLS),
#         "timestamp":  datetime.now(timezone.utc).isoformat()
#     }


# @app.get("/api/projects", tags=["Portfolio"])
# async def get_projects():
#     return {
#         "projects":  PROJECTS,
#         "total":     len(PROJECTS),
#         "highlight": [p for p in PROJECTS if p["highlight"]],
#         "timestamp": datetime.now(timezone.utc).isoformat()
#     }


# # ── Serve Frontend ────────────────────────────────────────────
# app.mount(
#     "/",
#     StaticFiles(directory="static", html=True),
#     name="static"
# )