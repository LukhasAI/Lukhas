# LUKHAS Innovation System Docker Container
FROM python:3.10-slim

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

# Copy application files
COPY . .

# Create necessary directories
RUN mkdir -p logs test_results data research_data visualizations

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV LOG_LEVEL=INFO

# Default command runs quick test
CMD ["python3", "src/test_innovation_quick_baseline.py"]

# Alternative commands:
# docker run lukhas-innovation python3 src/test_innovation_research_baseline.py  # Full test
# docker run lukhas-innovation python3 src/analyze_pass_rate_factors.py  # Analysis