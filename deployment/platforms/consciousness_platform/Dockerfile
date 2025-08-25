FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY consciousness_platform consciousness_platform
COPY examples examples

EXPOSE 8000

CMD ["python", "-m", "consciousness_platform.server"]
