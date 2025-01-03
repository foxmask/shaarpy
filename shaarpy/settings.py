"""
Django settings for shaarpy project.

Generated by 'django-admin startproject' using Django 5.0.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

import os
from pathlib import Path

import environ
from django.urls import reverse_lazy

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()

env_file_path = os.path.join(BASE_DIR, "shaarpy", ".env")
env_file = environ.Env.read_env(env_file_path)
env.read_env(env_file)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env.str("SECRET_KEY", default="!DONTFORGETTOCHANGETHISVALUE!")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool("DEBUG", default=False)  # set to False when using in production

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["127.0.0.1", "localhost"])

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "shaarpy",
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

ROOT_URLCONF = "shaarpy.urls"

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

WSGI_APPLICATION = "shaarpy.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": env.str("DB_ENGINE", default="django.db.backends.sqlite3"),
        "NAME": env.str("DB_NAME", default=BASE_DIR / "db.sqlite3"),
        "USER": env.str("DB_USER", default=""),
        "PASSWORD": env.str("DB_PASSWORD", default=""),
        "HOST": env.str("DB_HOST", default=""),
        "PORT": env.str("DB_PORT", default=""),
    },
    "TEST": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "shaarpy-test.sqlite3",
    },
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "%(asctime)s %(levelname)s %(module)s %(process)d %(message)s"
        },
        "simple": {"format": "%(levelname)s %(message)s"},
    },
    "filters": {"require_debug_false": {"()": "django.utils.log.RequireDebugFalse"}},
    "handlers": {
        "mail_admins": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler",
        },
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        "file": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": BASE_DIR / "shaarpy.log",
            "maxBytes": 61280,
            "backupCount": 3,
            "formatter": "verbose",
        },
    },
    "loggers": {
        "django.request": {
            "handlers": ["mail_admins", "file"],
            "level": "ERROR",
            "propagate": True,
        },
        "shaarpy.views": {
            "handlers": ["console", "file"],
            "level": "INFO",
        },
        "shaarpy.command": {
            "handlers": ["console", "file"],
            "level": "INFO",
        },
        "shaarpy.tools": {
            "handlers": ["console", "file"],
            "level": "INFO",
        },
    },
}

# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/
LANGUAGE_CODE = env.str("LANGUAGE_CODE", default="en-en")
TIME_ZONE = env.str("TIME_ZONE", default="UTC")
USE_I18N = env.bool("USE_I18N", default=True)
USE_TZ = env.bool("USE_TZ", default=True)

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

SECURE_CONTENT_TYPE_NOSNIFF = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "static"
MEDIA_ROOT = BASE_DIR / "media"

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CSRF_TRUSTED_ORIGINS = env.list(
    "CSRF_TRUSTED_ORIGINS", default=["https://*.mydomain.com"]
)

LOGOUT_REDIRECT_URL = reverse_lazy("home")

SHAARPY_AUTHOR = env.str("SHAARPY_AUTHOR", default="FoxMaSk")
SHAARPY_NAME = env.str("SHAARPY_NAME", default=f"ShaarPy - {SHAARPY_AUTHOR} Links")
SHAARPY_DESCRIPTION = env.str(
    "SHAARPY_DESCRIPTION", default="Share thoughts, links ideas, notes"
)
SHAARPY_ROBOT = env.str("SHAARPY_ROBOT", default="index, follow")
SHAARPY_LOCALSTORAGE_MD = env.str("SHAARPY_LOCALSTORAGE_MD", default="")
SHAARPY_STYLE = env.str("SHAARPY_STYLE", default="blue")
