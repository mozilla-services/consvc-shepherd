"""Settings, configuration and environment variables for consvc_shepherd."""

import sys
from pathlib import Path
from typing import Any

import environ
import markus
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

from consvc_shepherd.version import fetch_app_version_from_file

env = environ.Env(
    DEBUG=(bool, False),
    BOOSTR_API_JWT={str, None},
    OPENIDC_HEADER={str, None},
    OPENIDC_HEADER_PREFIX={str, None},
    IAP_AUDIENCE={str, None},
    SESSION_COOKIE_SECURE={bool, True},
    CSRF_COOKIE_SECURE={bool, True},
    SECURE_REFERRER_POLICY={str, "origin"},
    DJANGO_STATSD_ENABLED={bool, False},
    STATSD_DEBUG={bool, False},
    STATSD_HOST={str, "127.0.0.1"},
    STATSD_PORT={str, "8125"},
    STATSD_PREFIX={str, "shepherd"},
)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

environ.Env.read_env(BASE_DIR / ".env")

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY: str = env("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env("DEBUG")
BOOSTR_API_JWT = env.str("BOOSTR_API_JWT")
DEV_USER_EMAIL = "dev@example.com"
OPENIDC_HEADER = env("OPENIDC_HEADER")
OPENIDC_HEADER_PREFIX = env("OPENIDC_HEADER_PREFIX")
IAP_AUDIENCE = env("IAP_AUDIENCE")
ALLOWED_HOSTS: list[str] = ["*"]

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = env("SESSION_COOKIE_SECURE")
CSRF_COOKIE_SECURE = env("CSRF_COOKIE_SECURE")
SECURE_REFERRER_POLICY = env("SECURE_REFERRER_POLICY")

DJANGO_STATSD_ENABLED = env("DJANGO_STATSD_ENABLED")
STATSD_DEBUG = env("STATSD_DEBUG")
STATSD_ENABLED = DJANGO_STATSD_ENABLED or STATSD_DEBUG
STATSD_HOST = env("STATSD_HOST")
STATSD_PORT = env("STATSD_PORT")
STATSD_PREFIX = env("STATSD_PREFIX")

# Settings for django-countries. Contile AdvertiserUrl "geo" dropdown attribute.
# See: https://pypi.org/project/django-countries/#customization
# Contile advertisers list. Simply add the ISO 3166-1 country code to add as option.
COUNTRIES_ONLY: list[str] = [
    "AT",
    "AU",
    "BE",
    "BR",
    "CA",
    "CH",
    "DE",
    "ES",
    "FR",
    "GB",
    "IN",
    "JP",
    "IT",
    "JP",
    "LU",
    "MX",
    "NL",
    "PL",
    "SE",
    "SG",
    "US",
]
COUNTRIES_FIRST_SORT: bool = True

CONTILE_MAX_TILES = 8

# Application definition

INSTALLED_APPS: list[str] = [
    "polymorphic",
    "consvc_shepherd",
    "contile",
    "django.contrib.admin",
    "django.contrib.admindocs",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_countries",
    "dockerflow.django",
    "rest_framework",
    "corsheaders",
]

MIDDLEWARE: list = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "dockerflow.django.middleware.DockerflowMiddleware",
    "openidc.middleware.OpenIDCAuthMiddleware",
    "corsheaders.middleware.CorsMiddleware",
]

ROOT_URLCONF: str = "consvc_shepherd.urls"

TEMPLATES: list[dict[str, Any]] = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": ["./templates"],
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

WSGI_APPLICATION: str = "consvc_shepherd.wsgi.application"

# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES: dict[str, Any] = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": env("DB_NAME"),
        "USER": env("DB_USER"),
        "PASSWORD": env("DB_PASS"),
        "HOST": env("DB_HOST"),
        "PORT": "5432",
    }
}

# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE: str = "en-us"

TIME_ZONE: str = "UTC"

USE_I18N: bool = True

USE_TZ: bool = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_BUCKET_NAME = env("STATIC_BUCKET_NAME", default="")
STATIC_URL: str = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD: str = "django.db.models.BigAutoField"

STORAGES: dict[str, Any] = {
    "default": {
        "BACKEND": "storages.backends.gcloud.GoogleCloudStorage",
        "OPTIONS": {
            "bucket_name": env("GS_BUCKET_NAME", default=""),
        },
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

GS_BUCKET_FILE_NAME = env("GS_BUCKET_FILE_NAME", default="settings_from_shepherd")
ALLOCATION_FILE_NAME: str = env("ALLOCATION_FILE_NAME", default="allocation_file")

LOGGING: dict[str, Any] = {
    "version": 1,
    "formatters": {
        "json": {"()": "dockerflow.logging.JsonLogFormatter", "logger_name": "shepherd"}
    },
    "handlers": {
        "console": {
            "level": env("SHEPHERD_ENV", default="DEBUG"),
            "class": "logging.StreamHandler",
            "formatter": "json",
            "stream": sys.stdout,
        },
    },
    "loggers": {
        "shepherd": {
            "handlers": ["console"],
            "level": env("SHEPHERD_ENV", default="DEBUG"),
        },
        "request.summary": {
            "handlers": ["console"],
            "level": env("SHEPHERD_ENV", default="DEBUG"),
        },
        "markus": {"handlers": ["console"], "level": "DEBUG"},
        "sync_boostr_data": {
            "handlers": ["console"],
            "level": env("SHEPHERD_ENV", default="DEBUG"),
        },
    },
}

FORM_RENDERER = "django.forms.renderers.DjangoDivFormRenderer"

# Sentry Setup
SENTRY_DSN = env("SENTRY_DSN", default=None)
# Any of "release", "debug", or "disabled". Using "debug" will enable logging for Sentry.
SENTRY_MODE = env("SENTRY_MODE", default="disabled")
SENTRY_TRACE_SAMPLE_RATE = env("SENTRY_TRACE_SAMPLE_RATE", default=0)
SENTRY_ENV = env("SENTRY_ENV", default=None)

sentry_sdk.init(
    dsn=SENTRY_DSN,
    integrations=[
        DjangoIntegration(
            transaction_style="url",
            middleware_spans=True,
            signals_spans=False,
            cache_spans=True,
        )
    ],
    debug=SENTRY_MODE,
    environment=SENTRY_ENV,
    release=fetch_app_version_from_file().commit,
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # Disabled by default as not utilized currently. Extra cost.
    traces_sample_rate=SENTRY_TRACE_SAMPLE_RATE,
)

# Metrics Configuration
_MARKUS_BACKENDS: list[dict[str, Any]] = []
if DJANGO_STATSD_ENABLED:
    _MARKUS_BACKENDS.append(
        {
            "class": "markus.backends.datadog.DatadogMetrics",
            "options": {
                "statsd_host": STATSD_HOST,
                "statsd_port": STATSD_PORT,
                "statsd_prefix": STATSD_PREFIX,
            },
        }
    )
if STATSD_DEBUG:
    _MARKUS_BACKENDS.append(
        {
            "class": "markus.backends.logging.LoggingMetrics",
            "options": {
                "logger_name": "markus",
                "leader": "METRICS",
            },
        }
    )
markus.configure(backends=_MARKUS_BACKENDS)

# CORS_ORIGIN_ALLOW_ALL=True

CORS_ALLOWED_ORIGINS = [
    "http://0.0.0.0:5173",
]
