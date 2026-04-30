# Анализ производительности

Вариант: `photos-s18`  
Фактически измеряемые сервисы в текущем стенде: REST и gRPC для лайков из `week-15/starter`.

## Цель

Сравнить `latency` и `throughput` для двух реализаций:

- REST: `POST /api/likes` на `http://127.0.0.1:8080`
- gRPC: `LikesService/CreateLike` на `127.0.0.1:8174`

Тесты запускаются при разной конкуренции: `1`, `10`, `100`.

## Условия теста

- Docker Compose из `weeks/week-15/docker-compose.yml`
- REST-инструмент: `wrk`
- gRPC-инструмент: `ghz`
- Длительность одного прогона: `15s` или `30s`
- Payload REST: `{"target":"post_123"}`
- Payload gRPC: `{"target":"post_123"}`

## Команды запуска

Поднять сервисы:

```bash
cd "/home/nastya/Network software/weeks/week-15"
docker compose up -d --build
```

Запустить REST-тесты:

```bash
cd "/home/nastya/Network software/weeks/week-15/start"
chmod +x test_rest.sh test_grpc.sh
./test_rest.sh
```

Запустить gRPC-тесты:

```bash
cd "/home/nastya/Network software/weeks/week-15/start"
./test_grpc.sh
```

Если хотите прогнать только один уровень конкуренции:

```bash
./test_rest.sh 10
./test_grpc.sh 10
```

## Результаты

### REST

| Concurrency | Requests/sec | Avg Latency | P50 | P95 | P99 | 
|---|---:|---:|---:|---:|---|
| 1 | 1587.62 | 0.63 ms | 0.60 ms | - | 0.99 ms | 
| 10 | 3772.95 | 2.63 ms | 2.61 ms | - | 3.33 ms | 
| 100 | 4139.35 | 26.50 ms | 23.92 ms | - | 89.55 ms |

### gRPC

| Concurrency | Requests/sec | Avg Latency | P50 | P95 | P99 |
|---|---:|---:|---:|---:|---|
| 1 | 885.62 | 0.92 ms | 0.90 ms | 1.17 ms | 1.41 ms |
| 10 | 2590.30 | 3.71 ms | 3.42 ms | 5.18 ms | 5.98 ms |
| 100 | 2938.26 | 33.88 ms | 33.93 ms | 36.47 ms | 38.88 ms | 

## Анализ роста latency

- При увеличении concurrency `latency` обычно растет медленно до некоторого предела.
- После точки насыщения RPS почти перестает расти, а `latency` начинает увеличиваться резко.
- Для итогового вывода нужно сравнить, на каком уровне нагрузки это произошло у REST и у gRPC.

Пример интерпретации:

1. Пока `Requests/sec` растет почти пропорционально, сервер еще не насыщен.
2. Когда рост RPS замедляется, а `P95/P99 latency` резко увеличиваются, это и есть зона насыщения.
3. Если у gRPC при той же concurrency выше RPS и ниже P95/P99, значит для этого сценария он эффективнее REST.

## Точка насыщения

- REST:  c10-c100 RPS +10% (3773→4139), P99 x27! (3ms→89ms) - НЕстабилен

- gRPC: c10-c100 RPS +14% (2590→2938), P99 x6 (6ms→39ms)  - Стабильнее


Фактически по этим замерам (15s, localhost):

1. **Throughput**: REST выше на `c=1` (1587 RPS vs 886 RPS) и на `c=10`/`c=100` тоже немного выше (3773/4139 vs 2590/2938 RPS).
2. **Latency**:
   - на `c=1` REST и gRPC близки (sub-ms), gRPC немного быстрее по `P99` (1.41 ms vs 0.99 ms у REST — тут REST даже лучше по P99, но сравнение в пределах 1ms);
   - на `c=10` REST быстрее по `P99` (3.33 ms vs 5.98 ms);
   - на `c=100` оба деградируют, но у REST хвост тяжелее (`P99` 89.55 ms и max 732 ms), у gRPC `P99` 38.88 ms, но есть ошибки `Unavailable`.
3. **Насыщение**: около `c=100` для обоих сервисов (RPS почти плато, хвосты latency растут).
