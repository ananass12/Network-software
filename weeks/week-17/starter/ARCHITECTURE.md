# Архитектура

Проект: **events-s18**

## Обзор сервисов (3 микросервиса)

1. **Gateway** (FastAPI)
   - Внешняя точка входа.
   - REST: проксирует `GET/POST /api/events` в `events-svc-s18`.
   - GraphQL: `/graphql` с `Query.events` и `Mutation.createEvent`.

2. **events-svc-s18** (FastAPI + PostgreSQL)
   - Хранит события `event`: `id`, `title`, `location`, `created_at`.
   - Внешний REST **не торчит наружу**, доступен внутри docker-сети.

3. **events-grpc** (gRPC, package `events.v1`, service `EventsService`)
   - Внутренний сервис для валидации/нормализации `location`.

## Взаимодействие и протоколы

- **Client -> Gateway**: HTTP (REST/GraphQL).
- **Gateway -> events-svc-s18**: HTTP (REST) внутри сети.
- **events-svc-s18 -> events-grpc**: gRPC (быстро и удобно для внутренних контрактов).
- **events-svc-s18 -> PostgreSQL**: SQL.

## Хранилища данных

- **PostgreSQL**: таблица `events`.

## Ошибки

- Если `events-grpc` отклоняет `location`, `events-svc-s18` возвращает `400`.
- Если `events-grpc` недоступен, создание события вернёт ошибку (это сознательное упрощение для учебного проекта; в проде можно добавить fallback/очередь/ретраи).

## Запуск

`docker compose up --build`
