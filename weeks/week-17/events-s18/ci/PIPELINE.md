## CI/CD (описание)

Минимальный пайплайн для учебного проекта:

- **Lint**: запуск линтера/форматтера (например, `ruff`/`black`) для каждого сервиса.
- **Tests**: `make test WEEK=17` (проверка структуры/доков курса) + базовый smoke-test контейнеров.
- **Build**: `docker compose build` (сборка всех сервисов).

Деплой без простоя (на уровне идеи):

- **Kubernetes RollingUpdate** для `gateway` и `events-svc-s18`.
- **Readiness/Liveness** пробы (у нас есть `/health` у REST-сервисов).
- **Migration strategy**: в учебном проекте миграции упрощены (SQLAlchemy создаёт таблицы при старте),
  но в проде — отдельный job/step перед rollout.

