# ─────────────────────────────────────────────────────────────
# MecanjeoOps Dashboard — FastAPI Backend
# Platform Engineering Project — Mecandjeo Technology
# ─────────────────────────────────────────────────────────────

import os
import time
import platform
import psutil
from datetime import datetime, timezone
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# ─── App Initialization ───────────────────────────────────────
app = FastAPI(
    title="MecanjeoOps Dashboard",
    description="DevOps Status Dashboard — Mecandjeo Technology",
    version="1.0.0"
)

# ─── CORS Middleware ──────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Application Start Time ───────────────────────────────────
START_TIME = time.time()

# ─── Environment Config ───────────────────────────────────────
ENVIRONMENT = os.getenv("ENVIRONMENT", "dev")
PROJECT_NAME = os.getenv("PROJECT_NAME", "mecandjeo-infra")
AWS_REGION   = os.getenv("AWS_REGION", "us-east-1")
APP_VERSION  = os.getenv("APP_VERSION", "1.0.0")

# ─── Deployment History ───────────────────────────────────────
# In a real app this would come from a database
DEPLOYMENT_HISTORY = [
    {
        "version": "1.0.0",
        "status":  "success",
        "deployed_by": "github-actions",
        "message": "Initial release — MecanjeoOps Dashboard",
        "timestamp": "2026-04-25T10:00:00Z"
    },
    {
        "version": "0.9.0",
        "status":  "success",
        "deployed_by": "github-actions",
        "message": "Beta release — core API endpoints",
        "timestamp": "2026-04-20T14:30:00Z"
    },
    {
        "version": "0.8.0",
        "status":  "failed",
        "deployed_by": "github-actions",
        "message": "Health check misconfiguration — rolled back",
        "timestamp": "2026-04-18T09:15:00Z"
    },
    {
        "version": "0.7.0",
        "status":  "success",
        "deployed_by": "terraform",
        "message": "Infrastructure provisioned — ECS + ALB",
        "timestamp": "2026-04-15T16:45:00Z"
    },
]

# ─────────────────────────────────────────────────────────────
# API ROUTES
# ─────────────────────────────────────────────────────────────

@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint — used by ALB target group health checks.
    Must return 200 OK for ECS tasks to be marked healthy.
    """
    return JSONResponse(
        status_code=200,
        content={
            "status":      "healthy",
            "timestamp":   datetime.now(timezone.utc).isoformat(),
            "environment": ENVIRONMENT,
            "version":     APP_VERSION,
        }
    )


@app.get("/api/system", tags=["System"])
async def system_info():
    """
    Returns live system metrics — CPU, memory, uptime.
    """
    uptime_seconds = int(time.time() - START_TIME)
    uptime_hours   = uptime_seconds // 3600
    uptime_minutes = (uptime_seconds % 3600) // 60
    uptime_secs    = uptime_seconds % 60

    return {
        "cpu_percent":    psutil.cpu_percent(interval=0.1),
        "memory_percent": psutil.virtual_memory().percent,
        "memory_total_mb": round(
            psutil.virtual_memory().total / (1024 * 1024), 1
        ),
        "memory_used_mb": round(
            psutil.virtual_memory().used / (1024 * 1024), 1
        ),
        "uptime": f"{uptime_hours}h {uptime_minutes}m {uptime_secs}s",
        "uptime_seconds": uptime_seconds,
        "platform":       platform.system(),
        "python_version": platform.python_version(),
        "timestamp":      datetime.now(timezone.utc).isoformat(),
    }


@app.get("/api/infrastructure", tags=["Infrastructure"])
async def infrastructure_info():
    """
    Returns infrastructure metadata about this deployment.
    """
    return {
        "project":     PROJECT_NAME,
        "environment": ENVIRONMENT,
        "region":      AWS_REGION,
        "version":     APP_VERSION,
        "platform":    "AWS ECS Fargate",
        "runtime":     "Python FastAPI",
        "container_port": 8000,
        "iac_tool":    "Terraform",
        "registry":    "AWS ECR + Docker Hub",
        "timestamp":   datetime.now(timezone.utc).isoformat(),
    }


@app.get("/api/services", tags=["Services"])
async def services_status():
    """
    Returns status of key services in the infrastructure.
    """
    return {
        "services": [
            {
                "name":        "ECS Fargate",
                "status":      "operational",
                "description": "Container orchestration",
                "region":      AWS_REGION,
            },
            {
                "name":        "Application Load Balancer",
                "status":      "operational",
                "description": "Traffic distribution",
                "region":      AWS_REGION,
            },
            {
                "name":        "Amazon ECR",
                "status":      "operational",
                "description": "Container image registry",
                "region":      AWS_REGION,
            },
            {
                "name":        "S3 Remote State",
                "status":      "operational",
                "description": "Terraform state backend",
                "region":      AWS_REGION,
            },
            {
                "name":        "DynamoDB State Lock",
                "status":      "operational",
                "description": "Terraform state locking",
                "region":      AWS_REGION,
            },
            {
                "name":        "CloudWatch Logs",
                "status":      "operational",
                "description": "Container log aggregation",
                "region":      AWS_REGION,
            },
            {
                "name":        "Auto Scaling",
                "status":      "operational",
                "description": "CPU-based task scaling",
                "region":      AWS_REGION,
            },
        ],
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/api/deployments", tags=["Deployments"])
async def deployment_history():
    """
    Returns the deployment history timeline.
    """
    return {
        "deployments": DEPLOYMENT_HISTORY,
        "total":       len(DEPLOYMENT_HISTORY),
        "timestamp":   datetime.now(timezone.utc).isoformat(),
    }


@app.get("/api/stats", tags=["Stats"])
async def dashboard_stats():
    """
    Returns summary statistics for the dashboard header.
    """
    successful = sum(
        1 for d in DEPLOYMENT_HISTORY if d["status"] == "success"
    )
    failed = sum(
        1 for d in DEPLOYMENT_HISTORY if d["status"] == "failed"
    )
    return {
        "total_deployments": len(DEPLOYMENT_HISTORY),
        "successful":        successful,
        "failed":            failed,
        "success_rate":      f"{(successful/len(DEPLOYMENT_HISTORY)*100):.0f}%",
        "current_version":   APP_VERSION,
        "environment":       ENVIRONMENT,
        "timestamp":         datetime.now(timezone.utc).isoformat(),
    }


# ─── Serve Frontend ───────────────────────────────────────────
app.mount(
    "/",
    StaticFiles(directory="static", html=True),
    name="static"
)