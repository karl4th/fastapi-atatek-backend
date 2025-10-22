# Atatek API

Современный REST API для системы управления генеалогическими данными, построенный на FastAPI с использованием PostgreSQL и Redis.

## 🚀 Особенности

- **FastAPI** - современный, быстрый веб-фреймворк для создания API
- **PostgreSQL** - надежная реляционная база данных
- **Redis** - кэширование и управление сессиями
- **SQLAlchemy 2.0** - современная ORM с асинхронной поддержкой
- **Alembic** - миграции базы данных
- **Docker** - контейнеризация приложения
- **JWT аутентификация** - безопасная система авторизации
- **Pydantic** - валидация данных и сериализация

## 📋 Функциональность

### Аутентификация и пользователи
- Регистрация пользователей с верификацией по SMS
- JWT токены с refresh механизмом
- Управление ролями и правами доступа
- Профили пользователей с адресной информацией

### Система управления
- Управление ролями пользователей
- Система адресов с интеграцией OpenStreetMap
- Модерация контента

### Генеалогическое дерево
- Иерархическая структура семейного дерева
- Управление страницами профилей
- Система заявок на добавление/редактирование данных
- Модерация изменений

### Бизнес-логика
- Тарифные планы и подписки
- Персонализированные настройки пользователей

## 🛠 Технологический стек

- **Python 3.13**
- **FastAPI 0.119.1**
- **PostgreSQL** (через asyncpg)
- **Redis 6.4.0**
- **SQLAlchemy 2.0.44**
- **Alembic 1.17.0**
- **Pydantic 2.12.3**
- **PyJWT 2.10.1**
- **Uvicorn** (ASGI сервер)

## 📁 Структура проекта

```
backend/
├── src/app/
│   ├── api/v1/           # API endpoints
│   │   ├── auth.py       # Аутентификация
│   │   ├── system.py     # Системные функции
│   │   └── address.py    # Управление адресами
│   ├── config/           # Конфигурация
│   ├── core/             # Бизнес-логика
│   ├── db/               # Настройки БД
│   ├── models/           # SQLAlchemy модели
│   ├── schemas/          # Pydantic схемы
│   └── utils/            # Утилиты и декораторы
├── migration/            # Миграции Alembic
├── main.py              # Точка входа
├── requirements.txt     # Зависимости
├── docker-compose.yml   # Docker конфигурация
└── Dockerfile          # Образ приложения
```

## 🚀 Быстрый старт

### Предварительные требования

- Docker и Docker Compose
- Python 3.13+ (для локальной разработки)

### Запуск с Docker

1. **Клонируйте репозиторий:**
```bash
git clone <repository-url>
cd backend
```

2. **Запустите все сервисы:**
```bash
docker-compose up -d
```

3. **Примените миграции:**
```bash
docker-compose exec app alembic upgrade head
```

4. **API будет доступно по адресу:**
```
http://localhost:8000
```

### Локальная разработка

1. **Установите зависимости:**
```bash
pip install -r requirements.txt
```

2. **Настройте переменные окружения:**
```bash
export POSTGRES_HOST=localhost
export POSTGRES_USER=postgres
export POSTGRES_PASSWORD=postgres
export POSTGRES_DB=postgres
export REDIS_HOST=localhost
export JWT_SECRET_KEY=your_secret_key
```

3. **Запустите PostgreSQL и Redis:**
```bash
docker-compose up db redis -d
```

4. **Примените миграции:**
```bash
alembic upgrade head
```

5. **Запустите приложение:**
```bash
uvicorn main:app --reload
```

## 📚 API Документация

После запуска приложения документация доступна по адресам:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## 🔧 Конфигурация

Основные настройки находятся в `src/app/config/config.py`:

- `APP_VERSION` - версия приложения
- `DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME` - настройки PostgreSQL
- `REDIS_HOST` - настройки Redis
- `JWT_SECRET_KEY` - секретный ключ для JWT

## 🗄 База данных

### Основные модели

- **User** - пользователи системы
- **Role** - роли пользователей
- **Address** - адресная информация
- **Tree** - узлы генеалогического дерева
- **Page** - страницы профилей
- **Ticket** - заявки на изменения
- **Tariff** - тарифные планы
- **UserSubscription** - подписки пользователей

### Миграции

Для создания новой миграции:
```bash
alembic revision --autogenerate -m "описание изменений"
```

Для применения миграций:
```bash
alembic upgrade head
```

## 🔐 Аутентификация

API использует JWT токены с поддержкой refresh токенов. Токены передаются через HTTP-only cookies для безопасности.

### Основные endpoints:

- `POST /auth/signup` - регистрация
- `POST /auth/login` - вход в систему
- `POST /auth/signup/verify` - верификация по SMS
- `GET /auth/me` - получение данных текущего пользователя

## 🐳 Docker

### Сервисы

- **app** - основное приложение (порт 8000)
- **db** - PostgreSQL (порт 5432)
- **redis** - Redis (порт 6379)
- **adminer** - веб-интерфейс для БД (порт 8080)

### Полезные команды

```bash
# Просмотр логов
docker-compose logs -f app

# Выполнение команд в контейнере
docker-compose exec app bash

# Перезапуск сервиса
docker-compose restart app
```

## 🧪 Разработка

### Стандартизированные ответы

Все API endpoints используют декоратор `@standar_atatek`, который обеспечивает единообразный формат ответов:

```json
{
  "status": true,
  "data": { ... }
}
```

или в случае ошибки:

```json
{
  "status": false,
  "error": {
    "code": 400,
    "message": "Описание ошибки"
  }
}
```

### Структура кода

- **API слой** (`api/v1/`) - HTTP endpoints
- **Core слой** (`core/`) - бизнес-логика
- **Models** (`models/`) - SQLAlchemy модели
- **Schemas** (`schemas/`) - Pydantic схемы для валидации
- **Utils** (`utils/`) - вспомогательные функции и декораторы

## 📝 Лицензия

Этот проект является частной собственностью Atatek.

## 🤝 Поддержка

Для получения поддержки обращайтесь к команде разработки.

---

**Версия API:** 4.0.0
