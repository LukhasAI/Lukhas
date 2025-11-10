# Dockerfile for reproducible builds
FROM python:3.11-slim

RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir build in-toto cosign

# Set up a non-root user
RUN useradd -m builder
USER builder
WORKDIR /home/builder

# Copy source code
COPY . .

# Run the build
CMD ["python", "-m", "build"]
