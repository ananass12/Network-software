## Чек-лист безопасности (OWASP Top 10, 10–15 проверок)

1. **A01 Broken Access Control**: защищены ли операции изменения данных (create/update/delete) аутентификацией/авторизацией?
2. **A01 Broken Access Control**: нет ли IDOR (доступ к объектам по `id` без прав)?
3. **A02 Cryptographic Failures**: не передаются ли секреты/токены в query‑параметрах и логах?
4. **A03 Injection**: валидируется ли ввод (длина/формат строк), исключаются ли опасные символы/контент?
5. **A04 Insecure Design**: есть ли лимиты на ресурсы (rate limit, ограничения размера тела запроса)?
6. **A04 Insecure Design**: предусмотрено ли безопасное поведение по умолчанию (deny-by-default для write‑операций)?
7. **A05 Security Misconfiguration**: выключены ли лишние “dev‑фичи” (debug, подробные ошибки наружу)?
8. **A05 Security Misconfiguration**: настроены ли security headers (`HSTS`, `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, `CSP`)?
9. **A05 Security Misconfiguration**: ограничен ли `CORS` (разрешённые origin/методы/заголовки) и не стоит ли `*` без необходимости?
10. **A06 Vulnerable and Outdated Components**: фиксируются ли версии зависимостей и есть ли регулярная проверка на CVE (например, `pip-audit`)?
11. **A07 Identification & Authentication Failures**: где и как хранится секрет (API key) — не в коде, а в переменных окружения?
12. **A07 Identification & Authentication Failures**: есть ли защита от brute-force (rate limit/lockout) для auth‑механизма?
13. **A08 Software and Data Integrity Failures**: защищена ли цепочка поставки (зависимости, контейнер, CI), есть ли минимальные права в контейнере (non-root)?
14. **A09 Security Logging and Monitoring Failures**: ведутся ли безопасные логи (без секретов), есть ли request-id/корреляция и журналирование ошибок?
15. **A10 SSRF**: нет ли исходящих запросов по URL/host, управляемым пользователем (если появятся — allowlist и запрет private IP)?
