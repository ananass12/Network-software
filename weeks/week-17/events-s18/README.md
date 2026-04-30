# events-s18 (week-17 capstone)

Вариант: `variants/331/s18/week-17.json`, `project_code = events-s18`.

## Запуск

```bash
cd "weeks/week-17/events-s18"
docker compose up --build
```

После запуска:
- Gateway (внешний API): `http://localhost:8081`
- REST:
  - `GET  /api/events`
  - `POST /api/events` body: `{"title":"Meetup","location":"SPb"}`
  - `GET  /api/events/{id}`
- GraphQL: `POST http://localhost:8081/graphql`

Пример GraphQL запроса:

```bash
curl -sS http://localhost:8081/graphql \
  -H 'content-type: application/json' \
  -d '{"query":"query { events { id title location createdAt } }"}'
```

## Как остановить

```bash
docker compose down -v
```

## Краткая структура

- `gateway/`: внешний REST `/api/*` + GraphQL `/graphql`
- `events-svc/`: основной сервис событий (REST + Postgres)
- `events-grpc/`: внутренний gRPC (`events.v1.EventsService`) для валидации `location`
- `proto/`: контракт gRPC

