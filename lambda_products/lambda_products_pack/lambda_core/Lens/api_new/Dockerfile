FROM python:3.11-slim

WORKDIR /app

# Copy minimal project files
COPY . /app

# Create virtualenv inside container
RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --upgrade pip && \
    /opt/venv/bin/pip install -r requirements.txt || true

ENV PATH="/opt/venv/bin:$PATH"

EXPOSE 8000

CMD ["python", "cli.py", "--host", "0.0.0.0", "--port", "8000"]
