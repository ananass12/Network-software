FROM python:3.12-slim

WORKDIR /app

COPY events-grpc/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY events-grpc/ ./
COPY proto /app/proto

RUN python -m grpc_tools.protoc \
  -I /app/proto \
  --python_out=/app \
  --grpc_python_out=/app \
  /app/proto/events.proto

ENV GRPC_PORT=50051
EXPOSE 50051

CMD ["python", "main.py"]

