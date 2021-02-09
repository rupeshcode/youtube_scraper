'''
Django settings for care project.

Generated by 'django-admin startproject' using Django 2.0.5.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
'''

import os

from boilerplate import PROJECT_BASE_DIR
from celery.schedules import crontab
from pymodm import connect

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = PROJECT_BASE_DIR
DEBUG = True

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ['SECRET_KEY']

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'videos'
]

MIDDLEWARE = [
    'django.middleware.common.CommonMiddleware',
    'boilerplate.middlewares.request_validation.RequestValidationMiddleware',
    'boilerplate.middlewares.handle_exception.HandleExceptionMiddleware'
]

ROOT_URLCONF = 'boilerplate.urls'

WSGI_APPLICATION = 'boilerplate.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASE_SETTINGS = {
    'mongodb': {
        'NAME': os.environ.get('MONGO_DB_NAME', 'boilerplate'),
        'USER': os.environ.get('MONGO_DB_USER'),
        'PASS': os.environ.get('MONGO_DB_PASSWORD'),
        'HOST': os.environ.get('MONGO_DB_HOST', 'localhost'),
        'PORT': os.environ.get('MONGO_DB_PORT', '27017'),
    }
}

mongo_credentials = DATABASE_SETTINGS['mongodb']

connect(
    'mongodb://{userpass}{mongo_host}:{mongo_port}/{db}'.format(
        mongo_host=mongo_credentials.get('HOST'),
        mongo_port=str(mongo_credentials.get('PORT')),
        db=mongo_credentials.get('NAME'),
        userpass='{username}{password}{at}'.format(
            username=mongo_credentials.get('USER') or '',
            password=':' + mongo_credentials['PASS'] if mongo_credentials.get('PASS') else '',
            at='@' if mongo_credentials.get('USER') else ''
        )
    )
)


# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = []


# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = os.environ.get('TIMEZONE', 'UTC')

USE_I18N = True

USE_L10N = True

USE_TZ = True

REDIS_URL = (
    f"redis://{os.environ.get('REDIS_HOST')}"
    f":{os.environ.get('REDIS_PORT', '6379')}"
    f"/{str(os.environ.get('REDIS_DBNAME', 14))}"
)

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "CONNECTION_POOL_KWARGS": {"max_connections": 100, "retry_on_timeout": True},
            "SOCKET_CONNECT_TIMEOUT": 3
        },
        "KEY_PREFIX": "innote",
        "KEY_FUNCTION": "commons.utils.redis_manager.make_cache_key"
    }
}

CELERY_ENABLE_UTC = True
CELERY_TIMEZONE = os.environ.get('TIMEZONE', 'UTC')
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_SERIALIZER = 'json'
CELERY_CACHE_BACKEND = 'default'

CELERY_BEAT_SCHEDULE = {
    'fetch_videos': {
        'task': 'videos.tasks.fetch_videos',
        'schedule': crontab(minute=os.environ.get(
            'VIDEO_MINUTES', 10))
    }
}
