from ..base import *

DEBUG = True
SECRET_KEY = "django-insecure-local"
ALLOWED_HOSTS = []

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",  # обязательное поле
        "NAME": BASE_DIR / "db.sqlite3",         # путь к файлу базы
    }
}