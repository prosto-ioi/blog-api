"""
ASGI config for settings project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/asgi/
"""

import os
from decouple import config

os.environ.setdefault('DJANGO_SETTINGS_MODULE', f'settings.env.{config("BLOG_ENV_ID", default="local")}')

from django.core.asgi import get_asgi_application
application = get_asgi_application()