FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy ΛBot code
COPY quantum_consciousness_lambda_bot.py .
COPY master_lambda_bot_orchestrator.py .

# Create main application file
COPY main.py .

# Create non-root user
RUN useradd -m -u 1000 lambdabot && chown -R lambdabot:lambdabot /app
USER lambdabot

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8004/health || exit 1

# Set default port
ENV PORT=8004

# Run the application
CMD ["python", "main.py"]
