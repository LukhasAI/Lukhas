FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY memory_services memory_services
COPY examples examples

EXPOSE 8000

CMD ["python", "-m", "memory_services.server"]
