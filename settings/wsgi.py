import os
from decouple import config
from django.core.wsgi import get_wsgi_application

os.environ.setdefault(
    'DJANGO_SETTINGS_MODULE',
    f'settings.env.{config("BLOG_ENV_ID", default="local")}'
)
application = get_wsgi_application()