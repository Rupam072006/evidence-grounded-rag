# =============================================================================
# CMO Agent - Evidence-Grounded Decision Intelligence REST Microservice (Path B)
# Multi-stage production container image conforming to convergence specifications:
# - Base: Python 3.11-slim
# - Deterministic binary pinning (numpy==1.26.4)
# - Least-privilege non-root service account (cmo:cmo / UID 10001)
# - Fail-closed healthcheck probe targeting /health
# =============================================================================

FROM python:3.11-slim AS runtime

# Label metadata for OCI image governance
LABEL org.opencontainers.image.title="CMO Agent Path B Microservice" \
      org.opencontainers.image.description="Evidence-Grounded Marketing Intelligence & Decision-Support REST API" \
      org.opencontainers.image.version="2.0.0" \
      org.opencontainers.image.authors="Rhugved (Original Backend Lead), Pratik Bhuwad (Acting Delivery Lead)" \
      org.opencontainers.image.vendor="BHIV CMO Marketing Intelligence"

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    REPO_ROOT=/app \
    API_HOST=0.0.0.0 \
    API_PORT=8000 \
    ENVIRONMENT=production

# Install minimal system dependencies for health checks and security
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
        ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Create dedicated non-root runtime group and user
RUN groupadd -g 10001 cmo && \
    useradd -u 10001 -g cmo -m -s /bin/bash cmo

# Set working directory
WORKDIR /app

# Upgrade pip and install build tools
RUN pip install --upgrade pip setuptools wheel

# Install Python dependencies using pinned manifest
COPY requirements.txt pyproject.toml /app/
# Explicitly pin numpy 1.26.4 to ensure binary reproducibility
RUN pip install numpy==1.26.4 && \
    pip install -r requirements.txt

# Copy application source code and configurations
COPY configs/ /app/configs/
COPY data/ /app/data/
COPY src/ /app/src/

# Install the package in standard library path
RUN pip install --no-deps -e .

# Create writable runtime directories for non-root user
RUN mkdir -p /app/data/workflow_records /app/logs && \
    chown -R cmo:cmo /app

# Switch to non-root user
USER cmo:cmo

# Expose API microservice port
EXPOSE 8000

# Automated health probe verifying kernel and persistence readiness
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -f http://127.0.0.1:8000/health || exit 1

# Launch production ASGI server via Uvicorn
CMD ["uvicorn", "evidence_rag.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
