import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from datetime import timedelta

from django.conf.global_settings import MEDIA_ROOT, MEDIA_URL, STATICFILES_DIRS

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY")
# ВАЖНО:
# 1. АКТУАЛЬНЫЙ SECRET_KEY ДЛЯ ПРОЕКТА БЕРЕМ ИЗ СОЗДАННОГО ДЖАНГО settings.py КОМАНДОЙ "django-admin startproject config ."
# 2. ВСТАВЛЯЕМ ЭТОТ АКТУАЛЬНЫЙ SECRET_KEY В ФАЙЛ .env !!!
# ВАЖНО:
# ЕСЛИ ЗАБЫЛ SECRET_KEY - ЕГО МОЖНО СОЗДАТЬ:
# # config/secret_key_gen.py
# from django.core.management.utils import get_random_secret_key
# print(get_random_secret_key())

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    # ВАЖНО: ЕСЛИ МЕНЯЕШЬ АДМИНКУ/АВТОРИЗАЦИЮ, ТО !!!
    # - СВОИ ПРИЛОЖЕНИЯ admin/auth СТАВИШЬ === В НАЧАЛО ===
    # (т.е. = ПЕРЕД = "django.contrib.admin"/"django.contrib.auth")
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "django_filters",
    "rest_framework_simplejwt",
    "drf_yasg",
    # СЮДА ВВОДИ ИМЕНА СВОИХ ПРИЛОЖЕНИЙ
    "lms",
    "users",  # ВАЖНО: ПРИНЯТО ИМЕННО users!, а не user.
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": os.getenv("DATABASE_NAME"),
        "USER": os.getenv("DATABASE_USER"),
        "PASSWORD": os.getenv("DATABASE_PASSWORD"),
        "HOST": os.getenv("DATABASE_HOST"),
        "PORT": os.getenv("DATABASE_PORT", default="5432"),
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Europe/Moscow"

USE_I18N = True
USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = "static/"
# STATICFILES_DIRS = [BASE_DIR / "static"]  # Квадратные скобки обязательны, так как это список путей.

MEDIA_URL = "media/"
MEDIA_ROOT = os.path.join(
    BASE_DIR, "media"
)  # классический и надёжный вариант для MEDIA_ROOT. Подходит для старых версий Python/Django.
# MEDIA_ROOT = BASE_DIR / "media"  # современный и предпочтительный синтаксис (если проект использует pathlib). Эквивалентен os.path.join, но чище.


# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# ВАЖНО:
# НАДО СНЯТЬ КОММЕНТ НА AUTH_USER_MODEL, ЕСЛИ НАДО ДЕЛАТЬ НЕ СТАНДАРТНУЮ АУТЕНТИФИКАЦИЮ
# НАПРИМЕР: КОГДА ХОЧЕШЬ ЧЕРЕЗ ЭЛ.ПОЧТУ
AUTH_USER_MODEL = "users.User"

# Настройки JWT-токенов
REST_FRAMEWORK = {
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",  # 'rest_framework.permissions.AllowAny',
    ],
}

# Настройки срока действия токенов
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
}

# ВАЖНО:
# СНЯТЬ КОММЕНТЫ НИЖЕ ПО МЕРЕ НАПОЛНЕНИЯ ПРОЕКТА ШАГ ЗА ШАГОМ !!!
# ИНАЧЕ СЕРВЕР БУДЕТ РУГАТЬСЯ Т К В ПРОЕКТЕ НЕТ СООТВЕСТВУЮЩЕГО КОДА
# LOGIN_REDIRECT_URL = "/"
# LOGOUT_REDIRECT_URL = "/"
#
# # LOGIN_REDIRECT_URL = 'library:books_list'
# LOGIN_URL = "users:login"
#
# EMAIL_HOST = "smtp.yandex.ru"
# EMAIL_PORT = 465
# EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
# EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
# EMAIL_USE_TLS = False
# EMAIL_USE_SSL = True
#
# SERVER_EMAIL = EMAIL_HOST_USER
# DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
#
# CACHE_ENABLED = True
#
# if CACHE_ENABLED:
#     CACHES = {
#         "default": {"BACKEND": "django.core.cache.backends.redis.RedisCache", "LOCATION": "redis://localhost:6379"}
#     }
