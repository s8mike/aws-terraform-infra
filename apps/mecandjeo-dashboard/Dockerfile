# ─────────────────────────────────────────────────────────────
# MecanjeoOps Dashboard — Dockerfile
# Multi-stage build — non-root user — port 8000
# Security: apt-get upgrade applied to patch OS vulnerabilities
# ─────────────────────────────────────────────────────────────

FROM python:3.12-slim AS builder

# Apply OS security patches in builder stage
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /build
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --prefix=/install \
    --no-cache-dir -r requirements.txt

FROM python:3.12-slim AS production

# Apply OS security patches in production stage
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN groupadd -r appuser && \
    useradd -r -g appuser -d /app \
    -s /sbin/nologin appuser

WORKDIR /app
COPY --from=builder /install /usr/local
COPY --chown=appuser:appuser main.py .
COPY --chown=appuser:appuser static/ ./static/

USER appuser

ENV ENVIRONMENT=dev \
    APP_VERSION=1.0.0 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s \
  --start-period=30s --retries=3 \
  CMD python -c \
  "import urllib.request; \
   urllib.request.urlopen('http://localhost:8000/health')"

CMD ["uvicorn", "main:app", \
     "--host", "0.0.0.0", \
     "--port", "8000"]

#######################################################################################

# # ─────────────────────────────────────────────────────────────
# # MecanjeoOps Dashboard — Dockerfile
# # Multi-stage build for minimal production image
# # This version has security issues due to missing OS updates (no apt-get upgrade)
# # ─────────────────────────────────────────────────────────────

# # ── Stage 1: Builder ──────────────────────────────────────────
# FROM python:3.12-slim AS builder

# WORKDIR /build

# # Install dependencies into a local directory
# # This keeps the final image clean
# COPY requirements.txt .
# RUN pip install --upgrade pip && \
#     pip install --prefix=/install --no-cache-dir -r requirements.txt

# # ── Stage 2: Production Image ─────────────────────────────────
# FROM python:3.12-slim AS production

# # Create non-root user for security
# # Never run containers as root in production
# RUN groupadd -r appuser && \
#     useradd -r -g appuser -d /app -s /sbin/nologin appuser

# WORKDIR /app

# # Copy installed packages from builder stage
# COPY --from=builder /install /usr/local

# # Copy application code
# COPY --chown=appuser:appuser main.py .
# COPY --chown=appuser:appuser static/ ./static/

# # Switch to non-root user
# USER appuser

# # Environment variables with sensible defaults
# ENV ENVIRONMENT=dev \
#     PROJECT_NAME=mecandjeo-infra \
#     AWS_REGION=us-east-1 \
#     APP_VERSION=1.0.0 \
#     PYTHONUNBUFFERED=1 \
#     PYTHONDONTWRITEBYTECODE=1

# # Expose application port
# EXPOSE 8000

# # Health check for Docker and ECS
# HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
#   CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

# # Start the application
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]