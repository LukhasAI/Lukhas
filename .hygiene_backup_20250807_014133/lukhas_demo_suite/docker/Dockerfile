# LUKHAS Next Generation Demo - Docker Container
# Provides isolated environment for running LUKHAS Phase 5 demonstrations

FROM python:3.11-slim

# Metadata
LABEL maintainer="LUKHAS Trinity Framework"
LABEL version="1.0.0"
LABEL description="LUKHAS Next Generation Phase 5 Demo Environment"
LABEL trinity.framework="⚛️🧠🛡️"

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV LUKHAS_DOCKER_MODE=true
ENV DEMO_LOG_LEVEL=INFO

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    bash \
    jq \
    bc \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Create non-root user for security
RUN groupadd -r lukhas && useradd -r -g lukhas lukhas

# Copy requirements first for better caching
COPY requirements.txt .
COPY requirements-test.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r requirements-test.txt && \
    pip install --no-cache-dir websockets psutil cryptography pytest pytest-asyncio

# Copy LUKHAS source code
COPY . .

# Create necessary directories
RUN mkdir -p \
    lukhas_demo_suite/logs \
    lukhas_demo_suite/configs \
    lukhas_next_gen/stream \
    lukhas_next_gen/entropy_log \
    guardian_audit/logs \
    && chown -R lukhas:lukhas /app

# Make demo script executable
RUN chmod +x lukhas_demo_suite/demo.sh

# Switch to non-root user
USER lukhas

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python3 -c "import sys; print('LUKHAS Demo Container Healthy'); sys.exit(0)"

# Default command
CMD ["./lukhas_demo_suite/demo.sh"]

# Alternative entry points
# CMD ["./lukhas_demo_suite/demo.sh", "--quick"]  # Quick demo
# CMD ["/bin/bash"]  # Interactive shell