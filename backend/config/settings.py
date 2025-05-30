# backend/config/settings.py

import os
import sys
from pathlib import Path
from datetime import timedelta
import environ
from celery.schedules import crontab
from django.core.exceptions import ImproperlyConfigured
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from corsheaders.defaults import default_headers

# -----------------------------
# Environment Setup and Validation
# -----------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

# Initialize environment variables using django-environ
env = environ.Env(DEBUG=(bool, False))
environ.Env.read_env(env_file=os.path.join(BASE_DIR, '.env'))

# Validate required environment variables
required_env_vars = [
    'DJANGO_SECRET_KEY',
    'SIMPLE_JWT_SIGNING_KEY',
    'POSTGRES_DB',
    'POSTGRES_USER',
    'POSTGRES_PASSWORD',
]
missing_vars = [var for var in required_env_vars if not env(var, default=None)]
if missing_vars:
    raise ImproperlyConfigured(
        f"Missing required environment variables: {', '.join(missing_vars)}")

# -----------------------------
# Basic Settings
# -----------------------------

SECRET_KEY = env('DJANGO_SECRET_KEY')
DEBUG = env.bool('DEBUG', default=False)
ALLOWED_HOSTS = env.list('DJANGO_ALLOWED_HOSTS',
                         default=['localhost', '127.0.0.1', 'web'])

# =====================
# Kafka Configuration
# =====================

from kafka_app.constants import (
    TOPIC_MAPPINGS,
    USER_EVENTS,
    NOTIFICATIONS,
    ALBUM_EVENTS,
    COMMENT_EVENTS,
    FOLLOW_EVENTS,
    FRIEND_EVENTS,
    NEWSFEED_EVENTS,
    REACTION_EVENTS,
    SOCIAL_EVENTS,
    TAGGING_EVENTS,
    PHOTO_EVENTS,
    STORY_EVENTS,
    # You can add additional constants if needed
)

# Kafka broker URL for event-driven architecture
KAFKA_BROKER_URL = env('KAFKA_BROKER_URL', default='kafka:9092')
KAFKA_CONSUMER_GROUP_ID = env('KAFKA_CONSUMER_GROUP_ID',
                              default='centralized_consumer_group')

# Instead of parsing from an environment variable, now use pre-defined mapping
KAFKA_TOPICS = TOPIC_MAPPINGS

# Define the required topics (just a list of keys here)
REQUIRED_KAFKA_TOPICS = [
    USER_EVENTS,
    NOTIFICATIONS,
    ALBUM_EVENTS,
    COMMENT_EVENTS,
    FOLLOW_EVENTS,
    FRIEND_EVENTS,
    NEWSFEED_EVENTS,
    REACTION_EVENTS,
    SOCIAL_EVENTS,
    TAGGING_EVENTS,
    PHOTO_EVENTS,
    STORY_EVENTS,
    # Add any additional topics here...
]

# Check for missing Kafka topics
missing_topics = [topic for topic in REQUIRED_KAFKA_TOPICS if topic not in KAFKA_TOPICS]
if missing_topics:
    raise ImproperlyConfigured(
        f"Missing Kafka topics in KAFKA_TOPICS: {', '.join(missing_topics)}")

# Kafka encryption key for securing messages
KAFKA_ENCRYPTION_KEY = env('KAFKA_ENCRYPTION_KEY', default=None)

# -----------------------------
# Authentication Backends
# -----------------------------
AUTHENTICATION_BACKENDS = [
    'graphql_jwt.backends.JSONWebTokenBackend',
    'django.contrib.auth.backends.ModelBackend',
]


def is_running_tests():
    return 'test' in sys.argv


# -----------------------------
# Installed Applications
# -----------------------------
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
    'drf_spectacular_sidecar',
    'django_celery_beat',
    'csp',
    'graphene_django',
    'django_ratelimit',
    'graphql_jwt',
    'phonenumber_field',
    'django_filters',

    # Custom apps
    'users.apps.UsersConfig',
    'albums.apps.AlbumsConfig',
    'stories.apps.StoriesConfig',
    'tagging.apps.TaggingConfig',
    'reactions.apps.ReactionsConfig',
    'core.apps.CoreConfig',
    'notifications.apps.NotificationsConfig',
    'comments.apps.CommentsConfig',
    'friends.apps.FriendsConfig',
    'follows.apps.FollowsConfig',
    'messenger.apps.MessengerConfig',
    'newsfeed.apps.NewsfeedConfig',
    'social.apps.SocialConfig',
    'kafka_app.apps.KafkaAppConfig',
    'websocket.apps.WebSocketConfig',
]

# -----------------------------
# Middleware Configuration
# -----------------------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'csp.middleware.CSPMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'config.custom_error_middleware.CustomErrorMiddleware',
]

ROOT_URLCONF = 'config.urls'

# -----------------------------
# Templates
# -----------------------------
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
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
templates_dir = os.path.join(BASE_DIR, 'templates')
if not os.path.exists(templates_dir):
    os.makedirs(templates_dir)

# -----------------------------
# WSGI and ASGI Applications
# -----------------------------
WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

# -----------------------------
# Channels Configuration (Redis)
# -----------------------------
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [
                (
                    env('REDIS_HOST', default='redis'),
                    env.int('REDIS_PORT', default=6379))
            ],
        },
    },
}
CHANNELS_ALLOWED_HOSTS = [
    'localhost:3000',
    '127.0.0.1:3000',
    'frontend:3000',
]

REDIS_HOST = env('REDIS_HOST', default='redis')
REDIS_PORT = env.int('REDIS_PORT', default=6379)

# -----------------------------
# Database Configuration (PostgreSQL)
# -----------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('POSTGRES_DB'),
        'USER': env('POSTGRES_USER'),
        'PASSWORD': env('POSTGRES_PASSWORD'),
        'HOST': env('DB_HOST', default='db'),
        'PORT': env('DB_PORT', default='5432'),
        'CONN_MAX_AGE': 600,
        'TEST': {
            'NAME': 'test_' + env('POSTGRES_DB'),
            'ENGINE': 'django.db.backends.postgresql',
        },
    },
}
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# -----------------------------
# Password Validation
# -----------------------------
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
     'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# -----------------------------
# Internationalization
# -----------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# -----------------------------
# Static and Media Files
# -----------------------------
STATIC_URL = '/static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
ALLOWED_UPLOAD_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff']

# -----------------------------
# Custom User Model
# -----------------------------
AUTH_USER_MODEL = 'users.CustomUser'

# -----------------------------
# Django REST Framework Configuration
# -----------------------------
REST_FRAMEWORK = {
    'EXCEPTION_HANDLER': 'config.exception_handlers.custom_exception_handler',
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
}
if DEBUG:
    REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] = (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    )
else:
    REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] = (
        'rest_framework.renderers.JSONRenderer',
    )

# -----------------------------
# Simple JWT Configuration
# -----------------------------

SIMPLE_JWT_SIGNING_KEY = env('SIMPLE_JWT_SIGNING_KEY', default=None)
if not SIMPLE_JWT_SIGNING_KEY:
    raise ImproperlyConfigured("The SIMPLE_JWT_SIGNING_KEY environment variable must "
                               "be set for JWT security.")

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(
        hours=env.int('ACCESS_TOKEN_LIFETIME_HOURS', default=1)),
    'REFRESH_TOKEN_LIFETIME': timedelta(
        days=env.int('REFRESH_TOKEN_LIFETIME_DAYS', default=7)),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': env('SIMPLE_JWT_ALGORITHM', default='HS256'),
    'SIGNING_KEY': SIMPLE_JWT_SIGNING_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
}

# -----------------------------
# Djoser Configuration
# -----------------------------
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

# -----------------------------
# Spectacular (OpenAPI) Configuration
# -----------------------------
SPECTACULAR_SETTINGS = {
    'TITLE': 'Social Network APIs',
    'DESCRIPTION': 'API documentation for the Social Network project.',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': True,
    'SWAGGER_UI_DIST': 'https://cdn.jsdelivr.net/npm/swagger-ui-dist@latest',
    'SWAGGER_UI_FAVICON_HREF': 'https://cdn.jsdelivr.net/npm/swagger-ui-dist@latest/favicon-32x32.png',
    'COMPONENT_SPLIT_REQUEST': True,
    'SECURITY': [{'BearerAuth': []}],
    'COMPONENTS': {
        'securitySchemes': {
            'BearerAuth': {
                'type': 'http',
                'scheme': 'bearer',
                'bearerFormat': 'JWT',
            },
        },
    },
    'EXCLUDE_PATHS': [],
}

# -----------------------------
# CORS Configuration
# -----------------------------
CORS_ALLOWED_ORIGINS = env.list('CORS_ALLOWED_ORIGINS', default=[
    'http://127.0.0.1:3000',
    'http://localhost:3000',
    'http://frontend:3000',
])
CORS_ALLOW_METHODS = ["DELETE", "GET", "OPTIONS", "PATCH", "POST", "PUT"]
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = default_headers + (
    'Authorization',  # Allow the Authorization header for token-based requests
    "Content-Type",
    "X-Requested-With",
    "Accept",
    "X-Custom-Header"
)

# -----------------------------
# GraphQL Configuration
# -----------------------------
GRAPHENE = {
    'SCHEMA': 'schema.schema',
    'MIDDLEWARE': ['graphql_jwt.middleware.JSONWebTokenMiddleware'],
}
GRAPHQL_JWT = {
    'JWT_VERIFY_EXPIRATION': True,
    'JWT_EXPIRATION_DELTA': timedelta(hours=1),
    'JWT_REFRESH_EXPIRATION_DELTA': timedelta(days=7),
}
ENABLE_GRAPHQL_VALIDATION = env.bool('ENABLE_GRAPHQL_VALIDATION', default=True)
ENABLE_GRAPHQL_MIDDLEWARE = env.bool('ENABLE_GRAPHQL_MIDDLEWARE', default=True)

# -----------------------------
# Email Configuration
# -----------------------------
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = env('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = env.int('EMAIL_PORT', default=587)
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', default=True)
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')

# -----------------------------
# Celery Configuration
# -----------------------------
CELERY_BROKER_URL = env('CELERY_BROKER_URL', default='redis://redis:6379/0')
CELERY_RESULT_BACKEND = env('CELERY_RESULT_BACKEND', default='redis://redis:6379/0')
CELERY_ACCEPT_CONTENT = env.list('CELERY_ACCEPT_CONTENT', default=['json'])
CELERY_TASK_SERIALIZER = env('CELERY_TASK_SERIALIZER', default='json')
CELERY_RESULT_SERIALIZER = env('CELERY_RESULT_SERIALIZER', default='json')
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_TIMEZONE = 'UTC'
CELERY_BEAT_SCHEDULE = {
    'deactivate_expired_stories_every_hour': {
        'task': 'stories.tasks.deactivate_expired_stories',
        'schedule': crontab(minute=0, hour='*'),
    },
}

# -----------------------------
# Redis Caching
# -----------------------------
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': f'redis://{REDIS_HOST}:{REDIS_PORT}/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# -----------------------------
# Sentry Configuration
# -----------------------------
SENTRY_DSN = env('SENTRY_DSN', default='')
if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()],
        traces_sample_rate=1.0,
        send_default_pii=True
    )

# -----------------------------
# Content Security Policy (CSP)
# -----------------------------
CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = (
    "'self'", "https://apis.google.com", "https://cdn.jsdelivr.net", "'unsafe-inline'")
CSP_IMG_SRC = (
    "'self'", "https://images.unsplash.com", "https://cdn.jsdelivr.net", "data:")
CSP_STYLE_SRC = (
    "'self'", "https://fonts.googleapis.com", "https://cdn.jsdelivr.net",
    "'unsafe-inline'")
CSP_FONT_SRC = ("'self'", "https://fonts.gstatic.com")
CSP_CONNECT_SRC = ("'self'",)
CSP_BASE_URI = ("'self'",)
CSP_FORM_ACTION = ("'self'",)
CSP_REPORT_URI = '/csp-violation-report/'

# =====================
# Security Settings for Production Deployment
# =====================
if not DEBUG:
    # Enforce HTTPS for all requests
    SECURE_SSL_REDIRECT = True

    # Ensure cookies are only sent over HTTPS
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True

    # Protect against XSS attacks
    SECURE_BROWSER_XSS_FILTER = True

    # Prevent content sniffing by the browser
    SECURE_CONTENT_TYPE_NOSNIFF = True

    # Prevent clickjacking attacks
    X_FRAME_OPTIONS = 'DENY'

    # Enforce HTTP Strict Transport Security (HSTS)
    SECURE_HSTS_SECONDS = 31536000  # One year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

    # Configure referrer policy to limit sensitive data leakage
    SECURE_REFERRER_POLICY = 'no-referrer-when-downgrade'

    # Trust the X-Forwarded-Proto header for identifying HTTPS requests
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

    # Session settings
    SESSION_ENGINE = 'django.contrib.sessions.backends.cache'  # Store sessions in the cache
    SESSION_COOKIE_AGE = 1209600  # 2 weeks in seconds
    SESSION_EXPIRE_AT_BROWSER_CLOSE = True  # Sessions expire when the browser is closed

    # Additional headers for enhanced security
    SECURE_CROSS_ORIGIN_OPENER_POLICY = 'same-origin'  # Mitigate Spectre attacks
    SECURE_CROSS_ORIGIN_EMBEDDER_POLICY = 'require-corp'  # Protect against cross-origin embedding
    SECURE_CROSS_ORIGIN_RESOURCE_POLICY = 'same-origin'  # Prevent resource leaks to other origins

# =====================
# Internal IPs for Django Debug Toolbar
# =====================
INTERNAL_IPS = [
    '127.0.0.1',
    'localhost',
    'web',
]

# =====================
# Django Debug Toolbar Configuration
# =====================
DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': lambda request: DEBUG and not is_running_tests(),
    'INTERCEPT_REDIRECTS': False,
}

# =====================
# Logging Configuration
# =====================
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
            'level': 'INFO',  # Adjusted from DEBUG to INFO
            'filters': ['sanitize'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'level': 'INFO',
            'filters': ['sanitize'],
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'debug.log'),
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'channels': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',  # Adjusted to DEBUG for more detailed logs
            'propagate': True,
        },
        'core': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'kafka_app': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# =====================
# Additional Configurations (Commented Out)
# =====================

# Uncomment and configure as needed

# # Elasticsearch Configuration
# ELASTICSEARCH_DSL = {
#     'default': {
#         'hosts': env('ELASTICSEARCH_HOSTS', default='elasticsearch:9200'),
#     },
# }

# # Haystack Settings
# HAYSTACK_CONNECTIONS = {
#     'default': {
#         'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
#         'URL': 'http://127.0.0.1:9200/',
#         'INDEX_NAME': 'haystack_indexes',
#     },
# }
# HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'


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

# HAYSTACK_CONNECTIONS = {
#     'default': {
#         'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
#         'URL': 'http://localhost:9200/',
#         'INDEX_NAME': 'products',
#     },
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
