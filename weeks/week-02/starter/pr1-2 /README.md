# Практическое задание №1: Знакомство с Docker

## Структура

service/

├── main.py - файл FastAPI-сервиса.

├── schemas.py - модели данных.

├── requirements.txt - зависимости Python.

├── docker-compose.yml — запуск инфраструктуры.

├── .dockerignore - исключение лишних файлов.

└── Dockerfile - инструкция сборки контейнера.

## Сборка и запуск

- Сборка
  
```docker build -t inventory-service:v1.0 .```

или

```docker-compose build```

- Запуск
  
```docker run -d -p 8080:8000 --name inventory-app inventory-service:v1.0```

или

```docker-compose up -d``

- Проверка
  
```docker ps```

```docker logs inventory-app```

- Редакция данных

http://localhost:8080/docs


## Контрольные вопросы

1. Как работает изоляция Docker?

Использует:

namespaces — изоляция процессов, сети, файлов

cgroups — ограничение CPU, RAM, I/O

2. Почему Docker-образы immutable?

Образы не изменяются, пересборка = новый слой, гарантирует воспроизводимость и безопасность

3. VM vs Docker

VM	            

1.Полная ОС	     

2.Минуты запуска	 

3.Гигабайты	     

Docker

1.Общее ядро

2.Секунды

3.Мегабайты

4. Почему важен порядок Dockerfile?

Docker кэширует слои - зависимости копируются раньше кода, чтобы не переустанавливать их каждый раз

5. Роль requirements.txt

Фиксирует версии - одинаковая среда на всех машинах

6. Uvicorn vs WSGI

Uvicorn = ASGI - async - быстрее

WSGI = синхронный (Flask, Django old)

7. Проброс портов

```docker run -p 8080:8000```

Сначала порт компьютера, потом порт контейнера. Если порт занят - Docker выдаст ошибку

8. Просмотр логов

```docker logs inventory-app```

9. Передача env-переменных

```docker run -e DEBUG=true inventory-service```
