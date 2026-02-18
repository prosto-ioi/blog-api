from .env.local import *
from decouple import config, Csv

# read from env
SECRET_KEY =  config('BLOG_SECRET_KEY')
DEBUG = config('BLOG_DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('BLOG_ALLOWED_HOSTS',default='', cast=Csv())

# DB
DB_NAME = config('BLOG_DB_NAME', default='blog')
DB_USER = config('BLOG_DB_USER', default='postgres')
DB_PASSWORD = config('BLOG_DB_PASSWORD', default='')
DB_HOST = config('BLOG_DB_HOST', default='localhost')
DB_PORT = config('BLOG_DB_PORT', default='5432', cast=int)

# redis
REDIS_URL = config('BLOG_REDIS_URL', default='redis://localhost:6379/0')

# env now
ENV_ID = config('BLOG_ENV_ID', default='local')
