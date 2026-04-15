FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY *.py .

COPY client.py .
COPY service.py .
COPY service_pb2.py .
COPY service_pb2_grpc.py .

EXPOSE 8174
CMD ["python", "service.py"]
