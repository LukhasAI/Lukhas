# LUKHAS Innovation Research Package - Docker Container
FROM python:3.11-slim

# Metadata
LABEL maintainer="research@lukhas.ai"
LABEL version="1.0.0"
LABEL description="LUKHAS Innovation System - Research Package"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY tests/ ./tests/
COPY data/ ./data/

# Copy configuration files
COPY .env.example .env
COPY RESEARCH_MANIFEST.yaml .

# Create output directories
RUN mkdir -p test_results visualizations logs

# Set environment variables
ENV PYTHONPATH=/app
ENV RESEARCH_MODE=true
ENV SANDBOX_ONLY=true

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Default command runs tests
CMD ["python", "-m", "pytest", "tests/", "-v", "--tb=short"]