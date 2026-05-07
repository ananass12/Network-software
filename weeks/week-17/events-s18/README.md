# events-s18 

Вариант 18

## Запуск

```bash
cd "weeks/week-17/events-s18"
docker compose up --build
```

После запуска:
- Gateway (внешний API): `http://localhost:8081`
- gRPC: `localhost:50051`
- REST:
  - `GET  /api/events`
  - `POST /api/events` body: `{"title":"Meetup","location":"SPb"}`
  - `GET  /api/events/{id}`
- GraphQL: `POST http://localhost:8081/graphql`

Пример GraphQL запроса:

```bash
query { events { id title location createdAt } }
```

## Остановка

```bash
docker compose down -v
```

## Kubernetes (yaml манифесты)

Манифесты лежат в `k8s/`:
- `namespace.yaml`
- `config.yaml`
- `postgres.yaml`
- `apps.yaml`


## Краткая структура

- `gateway/` - внешний REST + GraphQL 
- `events-svc/` - основной сервис событий (REST + Postgres)
- `events-grpc/` - внутренний gRPC
- `proto/` - контракт gRPC
- `k8s/` - Kubernetes манифесты 