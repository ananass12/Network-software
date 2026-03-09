# Вопросы для самопроверки

1. В чем главное концептуальное отличие GraphQL от REST?

GraphQL — клиент определяет структуру и объем данных одним запросом. REST — сервер определяет фиксированные ресурсы по URL.

```
REST: GET /users/1 → всегда {id, name, email, posts, comments...}
GraphQL: { user(id:1) { name email } } → только name + email
```

2. Что такое Schema Definition Language (SDL)?

SDL — декларативный язык для описания типов данных, запросов и мутаций GraphQL API.

3. Чем Query отличается от Mutation? Могут ли они выполняться параллельно?

Query — чтение данных (getAllTickets, getTicket)

Mutation — изменение данных (createTicket, deleteTicket)

Параллельность:

- Несколько Query — выполняются параллельно (батч)

- Query + Query — параллельно  

- Mutation + Mutation — последовательно (изменения БД)

4. Что такое "резолвер" (resolver) и кто его вызывает?

Резолвер — функция, которая возвращает данные для конкретного поля схемы.

```
getAllTickets  - резолвер Query.get_all_tickets()
ticket.id     - резолвер Ticket.id (Ticket.from_db())
```

5. Как решается проблема N+1 запросов в GraphQL (dataloader)?

Проблема N+1:

- getAllTickets - [{id:1}, {id:2}, {id:3}]

- getUser(1) + getUser(2) + getUser(3) = N+1 запросов

DataLoader собирает все ID в кучу и делает один запрос.:

```
getUser([1,2,3]) - 1 запрос вместо N+1
```

6. Почему в GraphQL сложно реализовать кэширование на уровне HTTP (как в REST)?

REST — просто: 

```
GET /users/1 - всегда одинаковый ответ -кэшируем
```

GraphQL — сложно:

```
Запрос 1: { user(id:1) { name } }  - 3 поля
Запрос 2: { user(id:1) { name posts } }   - 5 полей  
Один URL, разные ответы - **не кэшируется**
```

В GraphQL клиент сам выбирает поля. Один endpoint, бесконечные варианты ответов = нет кэша.
