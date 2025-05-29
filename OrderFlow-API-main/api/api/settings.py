import os
import sys
from datetime import timedelta, timezone
from pathlib import Path
from celery.schedules import crontab
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv()

UTC = timezone.utc

ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1"
]

CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8000',
    'http://127.0.0.1:8000'
]

CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://127.0.0.1:3000'
]

CORS_ALLOW_CREDENTIALS = True

SECRET_KEY = os.getenv("SECRET_KEY", "django-insecure-your-secret-key-here")

DEBUG = True

# Отключаем SSL для локальной разработки
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_extensions",  
    "api_django",
    "rest_framework",
    "djoser",
    "users", 
    "channels",
    "aichat",
    "drf_yasg",
    "corsheaders",
    "social_django",
    "youmoney_app",
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware", 
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "api.urls"

TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [TEMPLATES_DIR],
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

WSGI_APPLICATION = "api.wsgi.application"
ASGI_APPLICATION = "api.asgi.application"  

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB_local", "db_for_api_django"),
        "USER": os.getenv("POSTGRES_USER_local", "postgres"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD_local", "Kohkau11999"),
        "HOST": os.getenv("DB_HOST_local", "localhost"),
        "PORT": os.getenv("DB_PORT_local", "5432"),
    }
}

# Используем SQLite для тестов
if 'test' in sys.argv:
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels.layers.InMemoryChannelLayer",
        },
    }
else:
    REDIS_HOST = os.getenv('REDIS_HOST', '127.0.0.1')
    REDIS_PORT = os.getenv('REDIS_PORT', '6379')
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG": {
                "hosts": [(REDIS_HOST, int(REDIS_PORT))],
            },
        },
    }

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

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC" 
USE_I18N = True
USE_L10N = True  
USE_TZ = True

STATIC_URL = "/static/"  
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=20),
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
}

AUTH_USER_MODEL = "users.User"  

DJOSER = {
    "SERIALIZERS": {
        "user_create": "users.serializers.CustomUserCreateSerializer",
    },
    'SEND_ACTIVATION_EMAIL': False,  
}

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.mail.ru"  
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "ukratitelkisok9913@inbox.ru")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "ubwtvq8jbcebqhCENdDM")
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

SWAGGER_SETTINGS = {
    "SECURITY_DEFINITIONS": {
        "Bearer": {
            "type": "apiKey",
            "in": "header", 
            "name": "Authorization",
            "description": "JWT Authorization header using the Bearer scheme. Example: 'Bearer <your_token>'",
        }
    },  
}
SWAGGER_USE_COMPAT_RENDERERS = False

SOCIAL_AUTH_YANDEX_OAUTH2_KEY = 'e54a436087b2456a9893e77d01592337'
SOCIAL_AUTH_YANDEX_OAUTH2_SECRET = '0b75eb2e67d04c8eaa011c59ac5bb2aa'

SOCIAL_AUTH_AUTHENTICATION_BACKENDS = (
    'social_core.backends.yandex.YandexOAuth2',
    'django.contrib.auth.backends.ModelBackend',  
)

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"redis://{REDIS_HOST}:{REDIS_PORT}/1", 
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}

CELERY_BROKER_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}/0'
CELERY_RESULT_BACKEND = f'redis://{REDIS_HOST}:{REDIS_PORT}/0'
CELERY_ACCEPT_CONTENT = ['json'] 
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'

CELERY_BEAT_SCHEDULE = {
    'update-cache-every-10-minutes': {
        'task': 'api_django.tasks.update_cache_periodically',
        'schedule': 60 * 10,
    },
    'daily-database-backup': {
        'task': 'api.tasks.backup_database',  
        'schedule': crontab(hour='2', minute='0'),
    },
}

#youmoney
YOOMONEY_ACCOUNT = os.getenv('YOOMONEY_ACCOUNT', '4100119070489003')
YOOMONEY_TOKEN = os.getenv('YOOMONEY_TOKEN', '4100119070489003.019887B7955A3768EF8669774D1114DC8E5B92441CAE8BC549648AF0DAD1C3141600147A0F633A9412884C5DAAC0EA08ECE95540516E197E7A83DDF207584E571863B17B5C9108160A8150B66E25A16BF8619A082CBFA099243B7DD08AAB834B4AAEE97ABF35E94881646C37EF0016CD61E757CB6653B933A0E03D9B0BF96793')
YOOMONEY_CLIENT_ID = os.getenv('YOOMONEY_CLIENT_ID', '580867D6094C1CF53943C4EC64BAC79688456853741E92665C3938CB6B6E421B')
YOOMONEY_REDIRECT_URL = os.getenv('YOOMONEY_REDIRECT_URL', 'http://localhost:8000/api/payments/success/')

LOG_DIR = os.path.join(BASE_DIR, 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOG_DIR, 'debug.log'),
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}