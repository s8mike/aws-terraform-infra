# Backend image: the FastAPI application plus the migration tooling, running as a normal (non-root) user.
FROM python:3.12-slim

WORKDIR /app

# Apply the operating system's available security fixes. Debian publishes fixes before the base image is rebuilt,
# so this closes the gap. Rebuild with --pull --no-cache to refresh them.
RUN apt-get update \
    && apt-get upgrade -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# A dedicated unprivileged user: if the application were ever compromised, it could not act as root in the container.
RUN groupadd --system app && useradd --system --gid app --no-create-home --shell /usr/sbin/nologin app

# Install the EXACT package versions recorded in requirements.lock (written by scripts/update_lock.sh from requirements.txt).
# Test-only packages live in requirements-dev.txt and are not installed in the image.
COPY requirements.lock .
RUN pip install --no-cache-dir -r requirements.lock

# The application code and the migration settings and history, owned by the unprivileged user.
COPY --chown=app:app app ./app
COPY --chown=app:app alembic.ini ./
COPY --chown=app:app migrations ./migrations

USER app

EXPOSE 8004

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8004"]