# backend/config/settings.py

import os
import sys
from pathlib import Path
from datetime import timedelta
import environ
from django.core.exceptions import ImproperlyConfigured
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

# Initialize environment variables using django-environ
BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env()
environ.Env.read_env(env_file=os.path.join(BASE_DIR, '.env'))

# Secret key used for cryptographic signing
SECRET_KEY = env('DJANGO_SECRET_KEY')
if not SECRET_KEY:
    raise ImproperlyConfigured("The DJANGO_SECRET_KEY environment variable is not set.")

# Debug mode, should be set to False in production
DEBUG = env.bool('DEBUG', default=False)

# List of allowed hosts that can make requests to this Django instance
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS',
                         default=['localhost', '127.0.0.1', 'web', 'backend'])

# =====================
# Kafka Configuration
# =====================

# Kafka broker URL for event-driven architecture
KAFKA_BROKER_URL = env('KAFKA_BROKER_URL', default='kafka:9092')
KAFKA_CONSUMER_GROUP_ID = env('KAFKA_CONSUMER_GROUP_ID',
                              default='centralized_consumer_group')

# Kafka topics for different events parsed from a comma-separated list
KAFKA_TOPICS_RAW = env('KAFKA_TOPICS', default='')
KAFKA_TOPICS = dict(
    item.split(':') for item in KAFKA_TOPICS_RAW.split(',') if ':' in item
)

# =====================
# Authentication Backends
# =====================
AUTHENTICATION_BACKENDS = [
    'graphql_jwt.backends.JSONWebTokenBackend',
    'django.contrib.auth.backends.ModelBackend',  # Default email/password backend
    # 'social_core.backends.google.GoogleOAuth2',
    # 'social_core.backends.facebook.FacebookOAuth2',
]


# Utility function to check if tests are currently running
def is_running_tests():
    return 'test' in sys.argv


# Installed applications (including PostgreSQL-backed apps)
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
    # 'django_elasticsearch_dsl',

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
    'websocket',  # WebSocket-related app
]

# Middleware configuration
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
]

# Root URL configuration
ROOT_URLCONF = 'config.urls'

# Template engine configuration
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        # Ensure templates directory is included
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                # Required by DRF and django-admin
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
            'hosts': [(env('REDIS_HOST', default='redis'),
                       env.int('REDIS_PORT', default=6379))],
        },
    },
}

REDIS_HOST = env('REDIS_HOST', default='redis')
REDIS_PORT = env.int('REDIS_PORT', default=6379)

# Database configuration using PostgreSQL for core functionalities
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

# Password validation settings
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 8}
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'
    },
]

# Internationalization settings
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static and media file settings
STATIC_URL = '/static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Custom user model
AUTH_USER_MODEL = 'users.CustomUser'

# Django REST Framework configuration
REST_FRAMEWORK = {
    'EXCEPTION_HANDLER': 'rest_framework.views.exception_handler',
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.IsAuthenticated',),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        # Enable Browsable API if DEBUG is True
        'rest_framework.renderers.BrowsableAPIRenderer' if DEBUG else 'rest_framework.renderers.JSONRenderer',
    ),
}

# Simple JWT configuration
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
}

# Djoser configuration
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

# CORS settings to allow frontend origins
CORS_ALLOWED_ORIGINS = env.list('CORS_ALLOWED_ORIGINS', default=[
    'http://127.0.0.1:3000', 'http://localhost:3000', 'http://frontend:3000'
])
CORS_ALLOW_CREDENTIALS = True

# GraphQl settings
GRAPHENE = {
    'SCHEMA': 'schema.schema',
    'MIDDLEWARE': [
        'graphql_jwt.middleware.JSONWebTokenMiddleware',
    ],
}


# Email configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = env('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = env.int('EMAIL_PORT', default=587)
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', default=True)
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')

# Celery configuration
CELERY_BROKER_URL = env('CELERY_BROKER_URL', default='redis://redis:6379/0')
CELERY_RESULT_BACKEND = env('CELERY_RESULT_BACKEND', default='redis://redis:6379/0')
CELERY_ACCEPT_CONTENT = env.list('CELERY_ACCEPT_CONTENT', default=['json'])
CELERY_TASK_SERIALIZER = env('CELERY_TASK_SERIALIZER', default='json')
CELERY_RESULT_SERIALIZER = env('CELERY_RESULT_SERIALIZER', default='json')
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_TIMEZONE = 'UTC'

# Redis caching configuration
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': f'redis://{REDIS_HOST}:{REDIS_PORT}/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Fetch SENTRY_DSN from the environment variables
SENTRY_DSN = env('SENTRY_DSN', default='')

# Initialize Sentry if DSN is provided
if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()],
        traces_sample_rate=1.0,
        send_default_pii=True
    )

# Content Security Policy (CSP) settings
CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = (
    "'self'", 'https://apis.google.com', 'https://cdn.jsdelivr.net', "'unsafe-inline'")
CSP_IMG_SRC = (
    "'self'", 'https://images.unsplash.com', 'https://cdn.jsdelivr.net', 'data:')
CSP_STYLE_SRC = (
    "'self'", 'https://fonts.googleapis.com', 'https://cdn.jsdelivr.net',
    "'unsafe-inline'")
CSP_FONT_SRC = ("'self'", 'https://fonts.gstatic.com')
CSP_CONNECT_SRC = ("'self'",)
CSP_BASE_URI = ("'self'",)
CSP_FORM_ACTION = ("'self'",)
CSP_REPORT_URI = '/csp-violation-report/'

# Security settings for production deployment
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

# Internal IPs for Django Debug Toolbar
INTERNAL_IPS = [
    '127.0.0.1',
    'localhost',
    'web',
]

# Django Debug Toolbar configuration
DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': lambda request: DEBUG and not is_running_tests(),
    'INTERCEPT_REDIRECTS': False,
}

# Logging configuration
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
            'level': 'INFO',
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

# # =====================
# # Elasticsearch Configuration
# # =====================
# ELASTICSEARCH_DSL = {
#     'default': {
#         'hosts': env('ELASTICSEARCH_HOSTS', default='localhost:9200'),
#     },
# }


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
