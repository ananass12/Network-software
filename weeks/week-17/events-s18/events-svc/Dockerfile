FROM python:3.12-slim

WORKDIR /app

COPY events-svc/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY events-svc/ ./
COPY proto /app/proto

RUN python -m grpc_tools.protoc \
  -I /app/proto \
  --python_out=/app \
  --grpc_python_out=/app \
  /app/proto/events.proto

ENV PORT=8277
EXPOSE 8277

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8277"]

