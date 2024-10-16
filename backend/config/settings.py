import os
import sys
from pathlib import Path
from datetime import timedelta
import environ
from django.core.exceptions import ImproperlyConfigured
from mongoengine import connect  # Import MongoEngine for MongoDB
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

# Initialize environment variables using django-environ
env = environ.Env(
    # Define default types and default values for environment variables
    DEBUG=(bool, False),
    DJANGO_SECRET_KEY=(str, ''),
    ALLOWED_HOSTS=(list, ['localhost', '127.0.0.1']),

    # PostgreSQL settings for Django ORM
    POSTGRES_DB=(str, 'app_db'),
    POSTGRES_USER=(str, 'app_user'),
    POSTGRES_PASSWORD=(str, 'app_password'),
    DB_HOST=(str, 'db'),
    DB_PORT=(str, '5432'),

    # MongoDB settings for apps using MongoEngine
    MONGO_DB_NAME=(str, 'social_db'),
    MONGO_HOST=(str, 'mongo'),  # Use Docker service name or localhost
    MONGO_PORT=(int, 27017),
    MONGO_USER=(str, ''),
    MONGO_PASSWORD=(str, ''),
    MONGO_AUTH_SOURCE=(str, 'admin'),

    # Redis and other settings
    CORS_ALLOWED_ORIGINS=(list, ['http://localhost:3000', 'http://127.0.0.1:3000']),
    REDIS_HOST=(str, 'redis'),
    REDIS_PORT=(int, 6379),
    EMAIL_HOST=(str, 'smtp.gmail.com'),
    EMAIL_PORT=(int, 587),
    EMAIL_USE_TLS=(bool, True),
    EMAIL_HOST_USER=(str, ''),
    EMAIL_HOST_PASSWORD=(str, ''),
    SENTRY_DSN=(str, ''),
    CELERY_BROKER_URL=(str, ''),
    CELERY_RESULT_BACKEND=(str, ''),
    KAFKA_BROKER_URL=(str, 'localhost:9092'),
    KAFKA_CONSUMER_GROUP_ID=(str, 'default_group'),
)

# Load environment variables from the .env file located in the project base directory
BASE_DIR = Path(__file__).resolve().parent.parent
environ.Env.read_env(env_file=os.path.join(BASE_DIR, '.env'))

# Secret key used for cryptographic signing
SECRET_KEY = env('DJANGO_SECRET_KEY')
if not SECRET_KEY:
    raise ImproperlyConfigured("The DJANGO_SECRET_KEY environment variable is not set.")

# Debug mode, should be set to False in production
DEBUG = env('DEBUG')

# List of allowed hosts that can make requests to this Django instance
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')

# Kafka settings for event-driven architecture
KAFKA_BROKER_URL = env('KAFKA_BROKER_URL')
KAFKA_CONSUMER_GROUP_ID = env('KAFKA_CONSUMER_GROUP_ID')
KAFKA_TOPICS = {
    'USER_EVENTS': 'user-events',
    'NOTIFICATIONS': 'user-notifications',
    # Add other events here...
}

# Authentication Backends
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',  # Default email/password backend
    'social_core.backends.google.GoogleOAuth2',  # Google OAuth2 backend
    'social_core.backends.facebook.FacebookOAuth2',  # Facebook OAuth2 backend
]


# Utility function to check if tests are currently running
def is_running_tests():
    return 'test' in sys.argv


# Installed applications (including both PostgreSQL-backed apps and MongoDB-backed apps)
INSTALLED_APPS = [
    # Django default apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party apps
    'rest_framework',
    'rest_framework_simplejwt.token_blacklist',
    'djoser',
    'corsheaders',
    'channels',
    'django_extensions',
    'drf_spectacular',
    'django_celery_beat',
    'csp',
    'django_elasticsearch_dsl',  # Elasticsearch support for searching content

    # Custom apps (Define here which apps use PostgreSQL and which use MongoDB)
    'users.apps.UsersConfig',  # PostgreSQL
    'albums.apps.AlbumsConfig',  # PostgreSQL
    'stories.apps.StoriesConfig',  # MongoDB via MongoEngine
    'tagging.apps.TaggingConfig',  # MongoDB via MongoEngine
    'reactions.apps.ReactionsConfig',  # PostgreSQL
    'core.apps.CoreConfig',  # Core utilities, often PostgreSQL

    # Kafka broker app
    'kafka_app.apps.KafkaAppConfig',
]

if DEBUG:
    INSTALLED_APPS += ['debug_toolbar']

# Middleware configuration
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'csp.middleware.CSPMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

if DEBUG:
    MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')

# Root URL configuration
ROOT_URLCONF = 'config.urls'

# Template engine configuration
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],  # List of directories to search for templates
        'APP_DIRS': True,  # Automatically search app directories
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# WSGI and ASGI application configuration
WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

# Channels configuration for WebSocket handling using Redis as a broker
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [(env('REDIS_HOST'), env('REDIS_PORT'))],
        },
    },
}

# Database configuration using PostgreSQL for core functionalities
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('POSTGRES_DB'),
        'USER': env('POSTGRES_USER'),
        'PASSWORD': env('POSTGRES_PASSWORD'),
        'HOST': env('DB_HOST'),
        'PORT': env('DB_PORT'),
        'CONN_MAX_AGE': 600,
        'TEST': {
            'NAME': 'test_' + env('POSTGRES_DB'),
            'ENGINE': 'django.db.backends.postgresql',
        },
    },
}

# MongoDB connection settings for apps using MongoEngine (like 'stories' and 'tagging')
connect(
    db=env('MONGO_DB_NAME'),
    username=env('MONGO_USER') or None,
    password=env('MONGO_PASSWORD') or None,
    host=env('MONGO_HOST'),
    port=int(env('MONGO_PORT')),
    authentication_source=env('MONGO_AUTH_SOURCE'),
)

# Password validation settings
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
     'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization settings
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True  # Removed USE_L10N as it's deprecated in Django 5.x

# Static and media file settings
STATIC_URL = '/static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Custom user model
AUTH_USER_MODEL = 'users.CustomUser'

# Django REST Framework configuration for API handling
REST_FRAMEWORK = {
    'EXCEPTION_HANDLER': 'config.exception_handlers.custom_exception_handler',
    'DEFAULT_AUTHENTICATION_CLASSES': (
    'rest_framework_simplejwt.authentication.JWTAuthentication',),
    'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.IsAuthenticated',),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_THROTTLE_CLASSES': (
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
        'users.throttling.SignupThrottle',
    ),
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/day',
        'user': '1000/day',
        'signup': '10/hour',
    },
}

# Simple JWT configuration for authentication
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=5),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
}

# Djoser configuration for user management APIs
DJOSER = {
    'LOGIN_FIELD': 'email',
    'USER_CREATE_PASSWORD_RETYPE': True,
    'USERNAME_CHANGED_EMAIL_CONFIRMATION': True,
    'PASSWORD_CHANGED_EMAIL_CONFIRMATION': True,
    'SEND_CONFIRMATION_EMAIL': True,
    'SET_USERNAME_RETYPE': True,
    'SET_PASSWORD_RETYPE': True,
    'ACTIVATION_URL': 'activate/{uid}/{token}',
    'SEND_ACTIVATION_EMAIL': True,
    'SERIALIZERS': {
        'user_create': 'users.serializers.CustomUserSerializer',
        'user': 'users.serializers.CustomUserSerializer',
        'current_user': 'users.serializers.CustomUserSerializer',
        'user_delete': 'djoser.serializers.UserDeleteSerializer',
    },
}

# Spectacular configuration for OpenAPI documentation
SPECTACULAR_SETTINGS = {
    'TITLE': 'Social Network APIs',
    'VERSION': '1.0.0',
    'COMPONENT_SPLIT_REQUEST': True,
    'SECURITY': [{'BearerAuth': []}],
    'COMPONENTS': {
        'securitySchemes': {
            'BearerAuth': {
                'type': 'http',
                'scheme': 'bearer',
                'bearerFormat': 'JWT'
            }
        }
    },
}

# CORS settings to allow frontend origins
CORS_ALLOWED_ORIGINS = env.list('CORS_ALLOWED_ORIGINS', default=[])

# Email configuration for sending out notifications
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = env('EMAIL_HOST')
EMAIL_PORT = env('EMAIL_PORT')
EMAIL_USE_TLS = env('EMAIL_USE_TLS')
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')

# Celery configuration for background task processing
CELERY_BROKER_URL = env('CELERY_BROKER_URL',
                        default=f'redis://{env("REDIS_HOST")}:{env("REDIS_PORT")}/0')
CELERY_RESULT_BACKEND = env('CELERY_RESULT_BACKEND',
                            default=f'redis://{env("REDIS_HOST")}:{env("REDIS_PORT")}/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'

# Celery Beat Schedule for periodic tasks
CELERY_BEAT_SCHEDULE = {
    'consume-user-events-every-5-seconds': {
        'task': 'kafka_app.tasks.consume_user_events',
        'schedule': 5.0,  # every 5 seconds
    },
    # Add other scheduled tasks as needed
}

# Redis Caching configuration
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': f'redis://{env("REDIS_HOST")}:{env("REDIS_PORT")}/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Sentry integration for error tracking and monitoring
SENTRY_DSN = env('SENTRY_DSN', default='')
if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()],
        traces_sample_rate=1.0,
        send_default_pii=True
    )

# Content Security Policy (CSP) settings
CSP_DEFAULT_SRC = ("'none'",)
CSP_SCRIPT_SRC = (
"'self'", 'https://apis.google.com', 'https://cdn.jsdelivr.net', "'unsafe-inline'")
CSP_IMG_SRC = (
"'self'", 'https://images.unsplash.com', 'https://cdn.jsdelivr.net', 'data:')
CSP_STYLE_SRC = (
"'self'", 'https://fonts.googleapis.com', 'https://cdn.jsdelivr.net', "'unsafe-inline'")
CSP_FONT_SRC = ("'self'", 'https://fonts.gstatic.com')
CSP_CONNECT_SRC = ("'self'",)
CSP_BASE_URI = ("'self'",)
CSP_FORM_ACTION = ("'self'",)
CSP_REPORT_URI = '/csp-violation-report/'

# Security settings for production deployment
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_REFERRER_POLICY = 'no-referrer-when-downgrade'
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Internal IPs for Django Debug Toolbar
INTERNAL_IPS = [
    '127.0.0.1',
    'localhost',
]

# Django Debug Toolbar configuration
DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': lambda request: DEBUG and not is_running_tests(),
    'INTERCEPT_REDIRECTS': False,
}

# Logging configuration to log to both console and file
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'sanitize': {
            '()': 'core.logging_filters.SensitiveDataFilter',
        },
    },
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'filters': ['sanitize'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'level': 'WARNING',
            'filters': ['sanitize'],
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'debug.log'),
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'WARNING',
            'propagate': True,
        },
        'channels': {
            'handlers': ['console', 'file'],
            'level': 'WARNING',
            'propagate': True,
        },
        'core': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'kafka_app': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

# Elasticsearch configuration
ELASTICSEARCH_DSL = {
    'default': {
        'hosts': 'localhost:9200'
    },
}

# from . import cron_jobs
# CRONJOBS = cron_jobs.CRONJOBS
#
#
#
# # TWILIO SETTINGS
# TWILIO_ACCOUNT_SID = config('TWILIO_ACCOUNT_SID')
# TWILIO_AUTH_TOKEN = config('TWILIO_TOKEN')
# TWILIO_FROM_NUMBER = config('TWILIO_FROM')
#
#
# # FCM (push notifications) configuration
# FCM_DJANGO_SETTINGS = {
#         "FCM_SERVER_KEY": config("FCM_SERVER_KEY"),
#          # true if you want to have only one active device per registered user at a time
#          # default: False
#         "ONE_DEVICE_PER_USER": True,
#          # devices to which notifications cannot be sent,
#          # are deleted upon receiving error response from FCM
#          # default: False
#         "DELETE_INACTIVE_DEVICES": False,
#
#
# ELASTICSEARCH_DSL_SIGNAL_PROCESSOR = 'django_elasticsearch_dsl.signals.RealTimeSignalProcessor'
# Elasticsearch configuration
# ELASTICSEARCH_DSL = {
#     'default': {
#         'hosts': 'localhost:9200'
#     },
# }

# HAYSTACK_CONNECTIONS = {
#     'default': {
#         'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
#         'URL': 'http://localhost:9200/',
#         'INDEX_NAME': 'products',
#     },
# }
# from elasticsearch_dsl import connections

# connections.configure(
#     default={'hosts': 'localhost'},
#     dev={
#         'hosts': ['localhost:9200'],
#         'sniff_on_start': True
#     }
# )
# # Name of the Elasticsearch index
# ELASTICSEARCH_INDEX_NAMES = {
#     'products/documents/product': 'products',
# }


# # Haystack Settings
# HAYSTACK_CONNECTIONS = {
#     'default': {
#         'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
#         'URL': 'http://127.0.0.1:9200/',
#         'INDEX_NAME': 'haystack_indexes',
#     },
# }
#
# HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'
#
