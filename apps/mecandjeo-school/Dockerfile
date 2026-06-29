FROM python:3.11-slim

LABEL maintainer="Mecandjeo Engineering Team"
LABEL project="Mecandjeo School Platform"
LABEL description="FastAPI backend for the Mecandjeo School Platform"
LABEL version="0.1.0"


WORKDIR /app

COPY requirements.txt .


RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

# Create a dedicated non-root user [Give user Bash as its login shell]
RUN useradd --create-home --shell /bin/bash schooluser 

# Give the application directory to the new user [Change ownership]
RUN chown -R schooluser:schooluser /app

# Switch to the non-root user
USER schooluser

# Network interface exposed by the Container
EXPOSE 8002

# How Docker determines whether the running application is healthy.
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8002/health')" || exit 1

# How the application restart
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002"]