# gRPC Streaming и Бенчмарки

## Задача
Одна из киллер-фич gRPC — это стриминг. Сервер может отвечать не одним сообщением, а потоком данных. Это идеально для лент новостей, логов, биржевых котировок или передачи больших файлов.
Также пора проверить, действительно ли gRPC так быстр, как о нем говорят.

## Ваш вариант
`variants/<GROUP>/<STUDENT_ID>/week-08.json`
Вам понадобится задание на streaming метод.

## Что нужно сделать
1. **Добавить Streaming метод**:
   - В `service.proto` добавьте новый метод с ключевым словом `stream` (Server Streaming).
   - Например: `rpc Subscribe(Request) returns (stream Update);`
   - Реализуйте этот метод на сервере: он должен возвращать итератор или использовать `yield` для отправки нескольких сообщений.
2. **Сравнить REST и gRPC**:
   - Напишите простой скрипт, который делает 1000 запросов к вашему REST сервису (из 1-2 недели) и 1000 запросов к gRPC сервису (Unary метод).
   - Замерьте время выполнения.
3. **Записать результаты**:
   - В файл `bench/results.md` запишите полученные цифры и ваши выводы.

## Что сдавать
1. Обновленный `.proto` и код сервера.
2. Скрипт бенчмарка.
3. Файл `bench/results.md` с отчетом.

## Как проверить
```bash
make test WEEK=08

python -m grpc_tools.protoc -Iproto --python_out=starter --grpc_python_out=starter proto/service.proto
```
В 1 терминале
```bash
docker compose build --no-cache

docker compose up --force-recreate
docker compose up -d
```
Во 2 терминале
```bash
python bench.py
```
