# LUKHAS Demo APIs Container
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy API implementations
COPY tools/scripts/create_dream_recall_api.py ./apis/
COPY tools/scripts/create_emotional_coherence_api.py ./apis/
COPY tools/scripts/create_memory_fold_api.py ./apis/
COPY tools/scripts/create_colony_consensus_api.py ./apis/
COPY tools/scripts/create_classical_dream_api.py ./apis/
COPY tools/scripts/create_classical_emotional_api.py ./apis/

# Copy launch script
COPY tools/scripts/docker/launch_demo_apis.py .

# Expose ports for all APIs
EXPOSE 8001 8002 8003 8004 8005 8006

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV LUKHAS_ENV=demo

# Launch all demo APIs
CMD ["python", "launch_demo_apis.py"]
