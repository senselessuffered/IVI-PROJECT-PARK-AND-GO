# Парк-и-Гоу

Веб-сервис бронирования гостевых парковочных мест в офисе: без двойных броней, с лимитами и напоминаниями.

## Запуск

### Docker

```bash
cp .env.example .env
docker compose up --build
```

- Приложение — <http://localhost:8000> (через nginx; статика отдаётся nginx)
- Почта (maildev) — <http://localhost:1080>
- Суперюзер для админки: `docker compose exec web python manage.py createsuperuser`
- Остановить: `docker compose down` (данные сохранятся; `down -v` — со сносом БД).

### Локально (приложение вне контейнера)

Postgres и maildev поднимаем в Docker, приложение — локально.

```bash
docker compose up -d db maildev
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
cp .env.example .env                                 # в .env: DB_HOST=localhost, EMAIL_HOST=localhost
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Тесты

```bash
docker compose exec web pytest
docker compose exec web pytest --cov=. --cov-report=term-missing
docker compose exec web ruff check .
```

## Ручки

| URL | Назначение | Доступ |
| --- | --- | --- |
| `/` | Редирект на список парковочных мест | все |
| `/spots/` | Список парковочных мест | все |
| `/spots/<id>/` | Детали места и актуальные бронирования | все |
| `/orders/` | Мои бронирования: поиск, пагинация | вошедший |
| `/orders/new/` | Создать бронь | вошедший |
| `/orders/<id>/` | Детали брони | вошедший |
| `/orders/<id>/edit/` | Редактировать бронь | владелец |
| `/orders/<id>/cancel/` | Отменить бронь (POST) | владелец |
| `/orders/<id>/delete/` | Удалить бронь | владелец |
| `/accounts/register/` | Регистрация | гость |
| `/accounts/login/` | Вход (по имени пользователя или email) | гость |
| `/accounts/logout/` | Выход (POST) | вошедший |
| `/private/admin/` | Django-админка | суперюзер |

Неавторизованного с любой ручки `/orders/…` редиректит на страницу входа с `?next=`.

## Стек и структура

- Python 3.13, Django 6, PostgreSQL 16, Bootstrap 5.
- Настройки разбиты по модулям: `application/settings/{base,database,auth,email}.py`.
- Общие поля моделей (`created_at`, `updated_at`) — в миксине `core.models.TimeStampedModel`.
- Зависимости и настройки инструментов описаны в `pyproject.toml`; Docker-образ ставит пакеты через `uv`.
- Конфигурация — только через `.env` (см. `.env.example`); `docker-compose.yml` берёт значения оттуда же.
