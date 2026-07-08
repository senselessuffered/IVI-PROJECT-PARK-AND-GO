# Парк-и-Гоу

Веб-сервис бронирования гостевых парковочных мест в офисе: без двойных броней, с лимитами и напоминаниями.

## Запуск

### Docker

```bash
cp .env.example .env
docker compose up --build
```

- Приложение — <http://localhost:8000>
- Почта (maildev) — <http://localhost:1080>
- Суперюзер для админки: `docker compose exec web python manage.py createsuperuser`
- Остановить: `docker compose down` (данные сохранятся; `down -v` — со сносом БД).

### Локально (SQLite)

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Ручки

| URL | Назначение | Доступ |
| --- | --- | --- |
| `/` | Список бронирований (главная), поиск, пагинация | все |
| `/booking/new/` | Создать бронь | вошедший |
| `/booking/<id>/` | Детали брони | все |
| `/booking/<id>/edit/` | Редактировать бронь | владелец |
| `/booking/<id>/cancel/` | Отменить бронь (POST) | владелец |
| `/booking/<id>/delete/` | Удалить бронь | владелец |
| `/spots/` | Список парковочных мест | все |
| `/accounts/register/` | Регистрация | гость |
| `/accounts/login/` | Вход | гость |
| `/accounts/logout/` | Выход (POST) | вошедший |
| `/admin/` | Django-админка | суперюзер |
