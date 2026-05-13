# ─────────────────────────────────────────────────────────────
# MecanjeoOps Portfolio — Dockerfile
# Multi-stage build — non-root user — port 8001
# ─────────────────────────────────────────────────────────────

FROM python:3.12-slim AS builder
WORKDIR /build
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --prefix=/install --no-cache-dir -r requirements.txt

FROM python:3.12-slim AS production
RUN groupadd -r appuser && \
    useradd -r -g appuser -d /app -s /sbin/nologin appuser

WORKDIR /app
COPY --from=builder /install /usr/local
COPY --chown=appuser:appuser main.py .
COPY --chown=appuser:appuser static/ ./static/

USER appuser

ENV ENVIRONMENT=dev \
    APP_VERSION=1.0.0 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

EXPOSE 8001

HEALTHCHECK --interval=30s --timeout=5s \
  --start-period=30s --retries=3 \
  CMD python -c \
  "import urllib.request; \
   urllib.request.urlopen('http://localhost:8001/health')"

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]