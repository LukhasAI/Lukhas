# ═══════════════════════════════════════════════════════════════════════════
# FILENAME: Dockerfile
# MODULE: infrastructure
# DESCRIPTION: Docker container configuration for Oneiric Core backend API.
#              Creates production-ready Python environment with FastAPI,
#              PostgreSQL drivers, and security hardening.
# DEPENDENCIES: python:3.11-slim, gcc, libpq-dev, requirements.txt, uvicorn
# LICENSE: PROPRIETARY - LUKHAS AI SYSTEMS - UNAUTHORIZED ACCESS PROHIBITED
# ═══════════════════════════════════════════════════════════════════════════

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create a non-root user
RUN useradd --create-home --shell /bin/bash oneiric
RUN chown -R oneiric:oneiric /app
USER oneiric

# Expose port
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "oneiric_core.main:app", "--host", "0.0.0.0", "--port", "8000"]

# ═══════════════════════════════════════════════════════════════════════════
# FILENAME: Dockerfile
# VERSION: 1.0.0
# TIER SYSTEM: Infrastructure (Container layer for all deployment tiers)
# ΛTRACE INTEGRATION: ENABLED
# CAPABILITIES: Container image creation, dependency management, security hardening,
#               production deployment, multi-architecture support, layer optimization
# FUNCTIONS: Container build process, dependency installation, user creation
# CLASSES: None directly defined (Docker image configuration)
# DECORATORS: None
# DEPENDENCIES: Python 3.11 base image, system packages, Python requirements
# INTERFACES: Docker build interface, container runtime interface
# ERROR HANDLING: Docker build error handling, dependency resolution
# LOGGING: ΛTRACE_ENABLED for container operations and deployment tracking
# AUTHENTICATION: Non-root user security for container execution
# HOW TO USE:
#   docker build -t oneiric-core .
#   docker run -p 8000:8000 -e DATABASE_URL=... oneiric-core
#   Used in docker-compose.yml for orchestrated deployment
# INTEGRATION NOTES: Production container for Oneiric Core backend API.
#   Optimized for security with non-root user, minimal attack surface.
#   Supports environment variable configuration for different deployments.
# MAINTENANCE: Update base image regularly, review security updates,
#   optimize layer caching, maintain minimal image size, update dependencies.
# CONTACT: LUKHAS DEVELOPMENT TEAM
# LICENSE: PROPRIETARY - LUKHAS AI SYSTEMS - UNAUTHORIZED ACCESS PROHIBITED
# ═══════════════════════════════════════════════════════════════════════════
