# Chat API
REST API для управления чатами и сообщениями. Система предназначена для создания чатов и обмена текстовыми сообщениями через API.

## Задача проекта

Создать простое и эффективное REST API, которое позволяет:
- Создавать новые чаты
- Отправлять сообщения в существующие чаты
- Получать информацию о чатах вместе с сообщениями
- Удалять чаты со всеми связанными сообщениями
- Предоставлять полную документацию API через Swagger/ReDoc

## Основные возможности

- Создание новых чатов
- Отправка сообщений в существующие чаты
- Получение чатов с последними сообщениями (с возможностью ограничения количества)
- Удаление чатов со всеми связанными сообщениями
- Автоматическая валидация данных на всех этапах
- Автоматическая документация через Swagger/ReDoc
- Админ-панель для управления чатами и сообщениями
- Логирование всех операций в файл
- Docker-контейнеризация для легкого развертывания

## Модели данных

### Чат (Chat)

- Название чата (1-200 символов)
- Дата создания (автоматически)

### Сообщение (Message)

- Текст сообщения (1-5000 символов)
- Ссылка на чат (ForeignKey)
- Дата создания (автоматически)

## Технологии

- Backend: Django 6.0 + Django REST Framework
- Database: PostgreSQL
- Documentation: Swagger/ReDoc (drf-yasg)
- Containerization: Docker + Docker Compose
- Environment: Python 3.12

## Deployment

**Проект может быть развернут локально или с использованием Docker. Доступные адреса:**

- API Endpoint: http://localhost:8000/api/
- Swagger UI: http://localhost:8000/swagger/
- ReDoc: http://localhost:8000/redoc/
- Admin Panel: http://localhost:8000/admin/

## Установка

### Способ 1: Локальная установка

**Клонировать репозиторий**
```bash
git clone https://github.com/erdes10032/chat.git
cd chat
```

**Создать виртуальное окружение**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows
```

**Установить зависимости**
```bash
cd chat_project
pip install -r requirements.txt
```

**Настроить переменные окружения**
```bash
# Linux/macOS
echo "SECRET_KEY=your_secret_key" >> .env # введите свой секретный ключ
echo "DEBUG=True" >> .env
echo "ALLOWED_HOSTS=localhost,127.0.0.1" >> .env
echo "POSTGRES_DB=chat" >> .env
echo "POSTGRES_USER=postgres" >> .env
echo "POSTGRES_PASSWORD=your_postgres_password" >> .env # введите свой пароль
echo "POSTGRES_PORT=5432" >> .env

#Windows
echo SECRET_KEY=your_secret_key >> .env # введите свой секретный ключ
echo DEBUG=True >> .env
echo ALLOWED_HOSTS=localhost,127.0.0.1 >> .env
echo POSTGRES_DB=chat >> .env
echo POSTGRES_USER=postgres >> .env
echo POSTGRES_PASSWORD=your_postgres_password >> .env # введите свой пароль
echo POSTGRES_PORT=5432 >> .env
```

**Создать базу данных в PostgreSQL**
```sql
CREATE DATABASE chat;
CREATE USER postgres WITH PASSWORD 'your_postgres_password'; -- введите свой пароль
GRANT ALL PRIVILEGES ON DATABASE chat TO postgres;
```

**Выполнить миграции**
```bash
python manage.py migrate
```

**Создать суперпользователя (опционально)**
```bash
python manage.py createsuperuser
```
**Запустить сервер**
```bash
python manage.py runserver
```

### Способ 2: Docker-установка

**Клонировать репозиторий**
```bash
git clone https://github.com/erdes10032/chat.git
cd chat\chat_project
```

**Запустить проект с помощью Docker Compose**
```bash
docker-compose up --build
```

**Остановить проект (опционально)**
```bash
docker-compose down
```

**Остановить проект с удалением volumes (опционально)**
```bash
docker-compose down -v
```

## API Документация

### Базовые методы

| Метод    | Эндпоинт | Описание |
|----------|----------|----------|
| `POST`   | `/api/chats/` | Создание нового чата |
| `GET`    | `/api/chats/{id}/` | Получение чата с сообщениями |
| `DELETE` | `/api/chats/{id}/` | Удаление чата со всеми сообщениями |
| `POST`   | `/api/chats/{id}/messages/` |  Отправка сообщения в чат |

### 1. Создание нового чата

**Метод: POST /api/chats/**

Описание: Создает новый чат с указанным названием

Пример запроса (curl):

```bash
curl -X POST "http://localhost:8000/api/chats/" \
     -H "Content-Type: application/json" \
     -d '{
           "title": "Общий чат команды"
         }'
```

Пример ответа - успех:

```json
{
  "id": 1,
  "title": "Общий чат команды",
  "created_at": "2024-01-20T10:30:00Z"
}
```

Пример ответа - ошибка:

```json
{
  "title": ["Это поле обязательно."]
}
```

### 2. Получение чата с сообщениями

**Метод: GET /api/chats/{id}/**

Описание: Возвращает информацию о чате вместе с последними сообщениями. Можно ограничить количество сообщений параметром limit

Пример запроса (curl) - получить чат:

```bash
curl -X GET "http://localhost:8000/api/chats/1/?limit=10"
```

Пример ответа:

```json
{
  "id": 1,
  "title": "Общий чат команды",
  "created_at": "2024-01-20T10:30:00Z",
  "messages": [
    {
      "id": 3,
      "chat": 1,
      "text": "Привет всем!",
      "created_at": "2024-01-20T10:35:00Z"
    },
    {
      "id": 2,
      "chat": 1,
      "text": "Добро пожаловать в чат!",
      "created_at": "2024-01-20T10:33:00Z"
    },
    {
      "id": 1,
      "chat": 1,
      "text": "Это наш первый чат",
      "created_at": "2024-01-20T10:31:00Z"
    }
  ]
}
```

### 3. Удаление чата

**Метод: DELETE /api/chats/{id}/**

Описание: Удаляет чат и все связанные с ним сообщения

Пример запроса (curl):

```bash
curl -X DELETE "http://localhost:8000/api/chats/1/"
```

Пример ответа - успех: HTTP 204 No Content

Пример ответа - ошибка:

```json
{
  "detail": "Чат не найден"
}
```

### 4. Отправка сообщения в чат

**Метод: POST /api/chats/{id}/messages/**

Описание: Отправляет новое сообщение в указанный чат

Пример запроса (curl):

```bash
curl -X POST "http://localhost:8000/api/chats/1/messages/" \
     -H "Content-Type: application/json" \
     -d '{
           "text": "Привет! Как дела?"
         }'
```

Пример ответа - успех:

```json
{
  "id": 4,
  "chat": 1,
  "text": "Привет! Как дела?",
  "created_at": "2024-01-20T10:40:00Z"
}
```

Пример ответа - ошибка:

```json
{
  "text": ["Это поле обязательно."]
}
```

### Коды ответов

- 200 - Успешный запрос (GET)
- 201 - Успешное создание (POST)
- 204 - Успешное удаление (DELETE, нет тела ответа)
- 400 - Ошибка валидации данных
- 404 - Чат не найден
- 405 - Метод не разрешен
- 500 - Внутренняя ошибка сервера

## Тестирование

```bash
# Если приложение запущено в докере, то нужно войти в контейнер
docker-compose exec web bash

# Запуск всех тестов
python manage.py test

# Запуск тестов с подробным выводом
python manage.py test --verbosity=2

# Запуск тестов конкретного приложения
python manage.py test chat_app

# Запуск конкретного класса тестов
python manage.py test chat_app.tests.ChatListViewTests

# Запуск конкретного теста
python manage.py test chat_app.tests.ChatListViewTests.test_create_chat_success
```

## Правила валидации и ограничения

### Для создания чата

- Название чата обязательно
- Минимальная длина названия: 1 символ
- Максимальная длина названия: 200 символов
- Пробелы по краям автоматически обрезаются

### Для отправки сообщения

- Текст сообщения обязателен
- Минимальная длина текста: 1 символ
- Максимальная длина текста: 5000 символов
- Пробелы по краям автоматически обрезаются
- Чат должен существовать

### Для получения чата

- Параметр limit необязательный
- Значение по умолчанию: 20 сообщений
- Минимальное значение: 1
- Максимальное значение: 100
- Некорректные значения заменяются на значение по умолчанию
- Сообщения возвращаются в порядке от новых к старым

## Технические детали

### Логирование

- Логи приложения пишутся в файл chat_api.log
- Логи Django выводятся в консоль
- Уровень логирования: DEBUG для файла, INFO для консоли

### Docker

- Два сервиса: web (Django) и db (PostgreSQL)
- Health check для базы данных
- Автоматическое определение среды (локальная/Docker)
- Volume для сохранения данных PostgreSQL

## Безопасность

- Нет аутентификации (разрешены все запросы)
- CSRF protection отключен для API
- Все данные валидируются перед сохранением
- SQL injection protection через ORM Django

## Пример использования

### Полный сценарий работы

**1. Создать чат:**

```bash
curl -X POST "http://localhost:8000/api/chats/" \
     -H "Content-Type: application/json" \
     -d '{"title": "Техническая поддержка"}'
```

**2. Отправить сообщения:**

```bash
# Первое сообщение
curl -X POST "http://localhost:8000/api/chats/1/messages/" \
     -H "Content-Type: application/json" \
     -d '{"text": "Здравствуйте! Чем могу помочь?"}'

# Второе сообщение
curl -X POST "http://localhost:8000/api/chats/1/messages/" \
     -H "Content-Type: application/json" \
     -d '{"text": "У меня проблема с авторизацией"}'
```

**3. Получить чат с сообщениями:**

```bash
curl -X GET "http://localhost:8000/api/chats/1/"
```

**4. Удалить чат:**

```bash
curl -X DELETE "http://localhost:8000/api/chats/1/"
```

## Администрирование

**Для доступа к админ-панели:**

- Создайте суперпользователя: python manage.py createsuperuser
- Перейдите по адресу: http://localhost:8000/admin/
- Войдите с созданными учетными данными

В админ-панели доступны:

- Просмотр списка чатов с поиском и фильтрацией
- Просмотр списка сообщений с превью текста
- Управление (добавление/редактирование/удаление) чатов и сообщений
