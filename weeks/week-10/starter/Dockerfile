FROM python:3.11-slim AS builder
# 1 builder - используется для установки зависимостей

WORKDIR /app 

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY requirements.txt . 

RUN pip install --upgrade pip && \
    pip install --no-cache-dir --prefix=/install -r requirements.txt


FROM python:3.11-slim AS runtime
# 2 runtime - в финальный образ копируются только установленные библиотеки из первого этапа и исходный код приложения

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/install/lib/python3.11/site-packages

COPY --from=builder /install /install
COPY . .

EXPOSE 8131

CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8131"]