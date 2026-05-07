# Архитектура

Проект: **events-s18**

## Цель проекта

Собрать учебную микросервисную систему, которая:
- предоставляет внешний API по REST и GraphQL;
- использует gRPC для внутреннего взаимодействия;
- хранит данные в PostgreSQL;
- запускается локально через Docker Compose;
- может быть развернута в Kubernetes по YAML-манифестам.

## Сервисы и ответственность

1. **gateway** (FastAPI, REST + GraphQL)
   - Внешняя точка входа для клиента.
   - REST-эндпоинты:
     - `GET /api/events`
     - `POST /api/events`
     - `GET /api/events/{id}`
   - GraphQL-эндпоинт:
     - `POST /graphql` (`Query.events`, `Mutation.createEvent`)
   - Не хранит собственные данные, только оркестрирует запросы к `events-svc-s18`.

2. **events-svc-s18** (FastAPI + PostgreSQL)
   - Основной доменный сервис событий.
   - Отвечает за CRUD-операции с таблицей `events`.
   - Перед сохранением вызывает `events-grpc` для проверки/нормализации `location`.
   - Доступен только внутри внутренней сети (не публикуется наружу как public endpoint).

3. **events-grpc** (gRPC, `events.v1.EventsService`)
   - Внутренний технический сервис.
   - Предоставляет gRPC-контракт для проверки/нормализации полей события.
   - Изолирует правила валидации от REST-слоя и может масштабироваться отдельно.

## Взаимодействие и протоколы

- **Client -> Gateway**: HTTP (REST/GraphQL).
- **Gateway -> events-svc-s18**: HTTP (REST) внутри сети.
- **events-svc-s18 -> events-grpc**: gRPC для внутреннего контракта.
- **events-svc-s18 -> PostgreSQL**: SQL.

## Модель данных

PostgreSQL, таблица `events`:
- `id`
- `title`
- `location`
- `created_at`

## Поток создания события

1. Клиент отправляет `POST /api/events` в `gateway`.
2. `gateway` проксирует запрос в `events-svc-s18`.
3. `events-svc-s18` вызывает `events-grpc`.
4. Если валидация не пройдена, возвращается `400`.
5. Если валидация успешна, запись сохраняется в PostgreSQL.
6. Ответ возвращается клиенту через `gateway`.

## Обработка ошибок

- При ошибке валидации возвращается `400` с объяснением.
- Для gRPC-вызова задан таймаут, чтобы сервис не зависал бесконечно.
- Если `events-grpc` недоступен, создание события завершается ошибкой (в учебной версии это допустимо).

## Инфраструктура

### Локально (Docker Compose)

- Поднимаются `postgres`, `events-grpc`, `events-svc-s18`, `gateway`.
- Порядок старта контролируется healthcheck и `depends_on`.
- Внешний доступ идет через `gateway` на порту `8081`.

### Kubernetes (YAML)

Манифесты находятся в `events-s18/k8s`:
- `namespace.yaml` - namespace `events-s18`;
- `config.yaml` - ConfigMap/Secret для переменных окружения;
- `postgres.yaml` - PVC + Deployment + Service для БД;
- `apps.yaml` - Deployment/Service для `events-grpc`, `events-svc-s18`, `gateway`.

## Запуск проекта

```bash
cd "weeks/week-17/events-s18"
docker compose up --build
```
# Архитектура

Проект: **events-s18**

## Цель проекта

Собрать учебную микросервисную систему, которая:
- предоставляет внешний API по REST и GraphQL;
- использует gRPC для внутреннего взаимодействия;
- хранит данные в PostgreSQL;
- запускается локально через Docker Compose;
- может быть развернута в Kubernetes по YAML-манифестам.

## Сервисы и ответственность

1. **gateway** (FastAPI, REST + GraphQL)
   - Внешняя точка входа для клиента.
   - REST-эндпоинты:
     - `GET /api/events`
     - `POST /api/events`
     - `GET /api/events/{id}`
   - GraphQL-эндпоинт:
     - `POST /graphql` (`Query.events`, `Mutation.createEvent`)
   - Не хранит собственные данные, только оркестрирует запросы к `events-svc-s18`.

2. **events-svc-s18** (FastAPI + PostgreSQL)
   - Основной доменный сервис событий.
   - Отвечает за CRUD-операции с таблицей `events`.
   - Перед сохранением вызывает `events-grpc` для проверки/нормализации `location`.
   - Доступен только внутри внутренней сети (не публикуется наружу как public endpoint).

3. **events-grpc** (gRPC, `events.v1.EventsService`)
   - Внутренний технический сервис.
   - Предоставляет gRPC-контракт для проверки/нормализации полей события.
   - Изолирует правила валидации от REST-слоя и может масштабироваться отдельно.

## Взаимодействие и протоколы

- **Client -> Gateway**: HTTP (REST/GraphQL).
- **Gateway -> events-svc-s18**: HTTP (REST) внутри сети.
- **events-svc-s18 -> events-grpc**: gRPC для внутреннего контракта.
- **events-svc-s18 -> PostgreSQL**: SQL.

## Модель данных

PostgreSQL, таблица `events`:
- `id` (PK)
- `title`
- `location`
- `created_at`

## Поток создания события

1. Клиент отправляет `POST /api/events` в `gateway`.
2. `gateway` проксирует запрос в `events-svc-s18`.
3. `events-svc-s18` вызывает `events-grpc`.
4. Если валидация не пройдена, возвращается `400`.
5. Если валидация успешна, запись сохраняется в PostgreSQL.
6. Ответ возвращается клиенту через `gateway`.

## Обработка ошибок

- При ошибке валидации возвращается `400` с объяснением.
- Для gRPC-вызова задан таймаут, чтобы сервис не зависал бесконечно.
- Если `events-grpc` недоступен, создание события завершается ошибкой (в учебной версии это допустимо).
- Для production-улучшения предусмотрены:
  - retry с backoff;
  - circuit breaker для зависимостей;
  - graceful degradation (например, асинхронная валидация через очередь).

## Инфраструктура

### Локально

- Поднимаются `postgres`, `events-grpc`, `events-svc-s18`, `gateway`.
- Порядок старта контролируется healthcheck и `depends_on`.
- Внешний доступ идет через `gateway` на порту `8081`.

### Kubernetes (YAML)

Манифесты находятся в `weeks/week-17/events-s18/k8s`:
- `namespace.yaml` - namespace `events-s18`;
- `config.yaml` - ConfigMap/Secret для переменных окружения;
- `postgres.yaml` - PVC + Deployment + Service для БД;
- `apps.yaml` - Deployment/Service для `events-grpc`, `events-svc-s18`, `gateway`.

## Запуск проекта

```bash
cd "weeks/week-17/events-s18"
docker compose up --build
```
