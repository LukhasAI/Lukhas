# LUKHAS AI Production Dockerfile
# Multi-stage build for optimized production image

# Build stage
FROM python:3.11-slim AS builder

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Copy source code
COPY . .

# Run tests and build checks
RUN python -m pytest tests/ --tb=short
RUN python tools/testing/coverage_metrics_system.py --quick-check

# Production stage
FROM python:3.11-slim AS production

# Create non-root user
RUN groupadd -r lukhas && useradd -r -g lukhas lukhas

# Set working directory
WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /root/.local /home/lukhas/.local

# Copy application code
COPY --chown=lukhas:lukhas . .

# Set Python path
ENV PATH=/home/lukhas/.local/bin:$PATH
ENV PYTHONPATH=/app

# Create necessary directories
RUN mkdir -p /app/logs /app/data && \
    chown -R lukhas:lukhas /app

# Switch to non-root user
USER lukhas

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Expose port
EXPOSE 8080

# Set environment variables
ENV ENVIRONMENT=production
ENV LOG_LEVEL=INFO
ENV PYTHONUNBUFFERED=1

# Default command
CMD ["python", "-m", "lukhas.serve", "--port", "8080", "--host", "0.0.0.0"]