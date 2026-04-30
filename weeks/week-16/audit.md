# Security Audit Report

## Объект аудита

- **project_code**: **devices-s18**
- **Проект**: `weeks/week-16/Service/` — FastAPI сервис `Inventory`
  - **REST**: CRUD по `/products/`
- **Хранилище**: in-memory список `products_db` (без БД и без пользователей)
- **Развёртывание**: `weeks/week-16/Service/docker-compose.yml` публикует порт `8080`

## Чек-лист (OWASP Top 10, 10–15 проверок)

- **A01 Broken Access Control**: защищены ли create/update/delete?
  - **До**: нет, любой клиент мог менять данные.
  - **После**: write‑эндпоинты защищены API key; доступ к объекту по `id` тоже требует ключ (минимизация IDOR).
- **A02 Cryptographic Failures**: не утекут ли секреты (в логах/URL)?
  - **До**: секретов нет, но при добавлении auth важно не логировать ключ.
  - **После**: API key берётся из env, в логи не пишется.
- **A03 Injection / Input validation**: валидируются ли поля и ограничены ли размеры?
  - **До**: любые строки/числа, риск DoS и некорректных данных.
  - **После**: Pydantic‑валидация (длины, диапазоны, allowlist для `quality`, pattern для текстовых полей).
- **A04 Insecure Design (DoS)**: есть ли rate limit и лимит размера тела?
  - **До**: нет.
  - **После**: in-memory rate limit + лимит тела запроса (и по `Content-Length`, и при его отсутствии через чтение body).
- **A05 Security Misconfiguration**: базовые security headers / CORS / trusted hosts
  - **До**: отсутствует.
  - **После**: добавлены security headers, CORS по allowlist, опционально TrustedHost; документацию можно отключать через env.
- **A06 Vulnerable and Outdated Components**: закреплены ли зависимости?
  - **После**: зависимости закреплены (pin) в `weeks/week-16/Service/requirements.txt`.
  - **Рекомендация**: добавить SCA (`pip-audit`) в CI для регулярной проверки CVE.
- **A07 Identification & Authentication Failures**: реализована ли аутентификация?
  - **До**: нет.
  - **После**: API key для write‑операций и чтения по `id` (минимально достаточный контроль).
- **A09 Security Logging & Monitoring**: есть ли безопасные логи (без секретов)?
  - **До**: логов нет.
  - **После**: request logging с request-id, без чувствительных данных.
- **A10 SSRF**: есть ли исходящие запросы по URL от пользователя?
  - Результат: нет (не применимо в текущем коде).

## Попытки “взломать себя”

- **Broken Access Control / IDOR**: без ключа запросы `POST/PUT/DELETE` и `GET /products/{id}` должны возвращать `401`.
- **DoS через большой payload**: запрос с большим телом должен быть отклонён (в т.ч. если клиент не прислал `Content-Length`).
- **Невалидный ввод**: слишком длинные строки/отрицательное количество должны давать `422`.
- **Проверка конфигурации**: при `INVENTORY_DISABLE_DOCS=1` `/docs` и `/openapi.json` должны быть недоступны.

Проверка реализована скриптом: `weeks/week-16/security_check.py`.