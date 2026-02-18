Blog API

REST API для блога с JWT-аутентификацией, кэшированием Redis, rate limiting и публикацией событий через Pub/Sub. Проект выполнен в рамках учебного задания.

тек технологий

- Backend: Django 6.0 + Django REST Framework
- База данных: PostgreSQL (разработка) / SQLite (локально)
- Аутентификация: JWT (djangorestframework-simplejwt)
- Кэширование и Pub/Sub: Redis + django-redis
- Rate limiting: django-ratelimit
- Логирование: встроенный модуль logging с ротацией файлов
- Версионирование: Git (ветки hw1 → main)


ERD

![ERD](Снимок экрана от 2026-02-18 19-13-10.png)

