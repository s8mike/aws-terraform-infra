# ===============================================
# # Wires the auth and user routers into the API.
# ===============================================
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request

from .config import AUTO_CREATE_SCHEMA, RUN_BOOTSTRAP
from .database import initialize_database
from .db.bootstrap import run_bootstrap

from .routes import (
    auth,
    admins,
    cranes,
    delay_logs,
    lookups,
    manager,
    operators,
    reports,
    shifts,
    task_logs,
    users,
    working_conditions,
)


# Start-up work, controlled by two separate settings:
#   AUTO_CREATE_SCHEMA creates the tables directly (local development only; elsewhere migrations build the schema).
#   RUN_BOOTSTRAP loads reference data, sample cranes and the first admin (safe to repeat).
@asynccontextmanager
async def application_lifespan(app: FastAPI):
    if AUTO_CREATE_SCHEMA:
        initialize_database()
    if RUN_BOOTSTRAP:
        run_bootstrap()
    yield


# Create the FastAPI application with the public service name.
app = FastAPI(
    title="Mecandjeo MHC Monitoring",
    version="0.1.0",
    lifespan=application_lifespan,
)


# Add lightweight browser/security headers to every HTTP response.
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    return response


# Health check used by Docker, load balancers, and deployment validation.
@app.get("/health")
def health():
    return {"status": "ok"}


# Root endpoint confirms the service identity and points users to API docs.
@app.get("/")
def home():
    return {
        "application": "Mecandjeo MHC Monitoring",
        "status": "running",
        "docs": "/docs",
    }


# Register authentication and account routes.
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/users", tags=["users"])

# Register Phase 6 admin configuration and MHC asset management routes.
app.include_router(admins.router, prefix="/api/admin", tags=["admin"])
app.include_router(cranes.router, prefix="/api/cranes", tags=["cranes"])

# Register Phase 4 operator workflow routes.
app.include_router(operators.router, prefix="/api/operators", tags=["operators"])
app.include_router(shifts.router, prefix="/api/shifts", tags=["shifts"])
app.include_router(task_logs.router, prefix="/api/task-logs", tags=["task-logs"])
app.include_router(delay_logs.router, prefix="/api/delay-logs", tags=["delay-logs"])
app.include_router(
    working_conditions.router,
    prefix="/api/working-conditions",
    tags=["working-conditions"],
)

# Register Phase 5 manager dashboard and analysis routes.
app.include_router(manager.router, prefix="/api/manager", tags=["manager"])

# Register Phase 7 historical reporting and CSV export routes.
app.include_router(reports.router, prefix="/api/reports", tags=["reports"])

# Register Phase 9 read-only lookup values for operator, manager, and admin forms.
app.include_router(lookups.router, prefix="/api/lookups", tags=["lookups"])