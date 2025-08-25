FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY dream_commerce dream_commerce
COPY examples examples

EXPOSE 8000

CMD ["python", "-m", "dream_commerce.server"]
