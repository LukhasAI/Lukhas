# LUKHAS AI Production Docker Image
# Optimized for Azure Container Apps with GitHub Student Pack
# ===================================================
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt ./
RUN test -f requirements-test.txt && cp requirements-test.txt ./ || echo "No test requirements"

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user for security
RUN useradd -m -u 1000 lukhas && \
    chown -R lukhas:lukhas /app

USER lukhas

# Expose production API port
EXPOSE 8080

# Health check for production API
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Environment variables for production
ENV PYTHONPATH=/app
ENV LUKHAS_PRODUCTION=true
ENV LUKHAS_API_HOST=0.0.0.0
ENV LUKHAS_API_PORT=8080

# Start the production LUKHAS AI system
CMD ["python", "production_main.py"]
