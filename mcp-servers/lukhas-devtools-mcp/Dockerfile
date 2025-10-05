FROM python:3.12-slim
WORKDIR /app
COPY . /app
RUN pip install numpy scipy pyyaml
ENTRYPOINT ["python","server.py"]