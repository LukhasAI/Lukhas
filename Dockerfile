# LUKHAS AI Production Dockerfile
# Multi-stage build for optimized production deployment

# Build stage
FROM python:3.11-slim as builder

# Set build-time environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies for building
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and install Python dependencies
COPY requirements.txt requirements-core.txt ./
RUN pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt && \
    pip install -r requirements-core.txt

# Production stage
FROM python:3.11-slim as production

# Set production environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH" \
    LUKHAS_ENVIRONMENT=production \
    LUKHAS_LOG_LEVEL=INFO

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Create lukhas user for security
RUN groupadd -r lukhas && useradd -r -g lukhas lukhas

# Create application directory
WORKDIR /app

# Copy application code with proper ownership
COPY --chown=lukhas:lukhas . .

# Create necessary directories
RUN mkdir -p /app/logs /app/data /app/trace && \
    chown -R lukhas:lukhas /app

# Switch to non-root user
USER lukhas

# Expose port for LUKHAS AI API
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Set entrypoint and default command
ENTRYPOINT ["python", "-m"]
CMD ["lukhas.main"]