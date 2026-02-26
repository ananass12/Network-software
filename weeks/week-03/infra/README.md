# Практическое задание №3: Единая точка входа (API Gateway)

## Структура

pr3/

│

├ docker-compose.yml — запуск инфраструктуры.

├ nginx.conf - маршрутизация между микросервисами.

│

├ service1/

│   ├ schemas.py - модели данных.

│   ├ requirements.txt - зависимости Python.

│   ├ .dockerignore - исключение лишних файлов.

│   ├ main.py - файл FastAPI-сервиса 1.

│   └ Dockerfile - инструкция сборки контейнера.

│

└ service2/

    ├ requirements.txt - зависимости Python.

    ├ .dockerignore - исключение лишних файлов.

    ├ main.py - файл FastAPI-сервиса 2.
    
    └ Dockerfile - инструкция сборки контейнера.


## Команды

```docker-compose up --build``

```docker-compose down```

## Проверка

```make test WEEK=03```

http://localhost:8080/api/tasks

http://localhost:8080/api/other