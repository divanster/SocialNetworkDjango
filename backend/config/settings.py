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
env = environ.Env(
    # Define default types and default values for environment variables
    DEBUG=(bool, False),
    DJANGO_SECRET_KEY=(str, ''),
    ALLOWED_HOSTS=(list, ['localhost', '127.0.0.1']),
    POSTGRES_DB=(str, 'app_db'),
    POSTGRES_USER=(str, 'app_user'),
    POSTGRES_PASSWORD=(str, 'app_password'),
    DB_HOST=(str, 'db'),
    DB_PORT=(str, '5432'),
    CORS_ALLOWED_ORIGINS=(list, ['http://localhost:3000', 'http://127.0.0.1:3000']),
    REDIS_HOST=(str, 'redis'),  # Defaults for Redis
    REDIS_PORT=(int, 6379),  # Defaults for Redis
    EMAIL_HOST=(str, 'smtp.gmail.com'),  # Defaults for Email
    EMAIL_PORT=(int, 587),  # Defaults for Email
    EMAIL_USE_TLS=(bool, True),  # Defaults for Email
    EMAIL_HOST_USER=(str, ''),  # Defaults for Email user
    EMAIL_HOST_PASSWORD=(str, ''),  # Defaults for Email password
    SENTRY_DSN=(str, ''),  # Default for Sentry DSN
    CELERY_BROKER_URL=(str, ''),  # Default for Celery Broker URL
    CELERY_RESULT_BACKEND=(str, ''),  # Default for Celery Result Backend
    KAFKA_BROKER_URL=(str, 'localhost:9092'),  # Default for Kafka
    KAFKA_CONSUMER_GROUP_ID=(str, 'default_group'),  # Added consumer group ID
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

# Kafka settings
KAFKA_BROKER_URL = env('KAFKA_BROKER_URL')
KAFKA_CONSUMER_GROUP_ID = env('KAFKA_CONSUMER_GROUP_ID')
KAFKA_TOPICS = {
    'USER_EVENTS': 'user-events',
    'NOTIFICATIONS': 'user-notifications',
    'ALBUM_EVENTS': 'album-events',
    'COMMENT_EVENTS': 'comment-events',
    'FOLLOW_EVENTS': 'follow-events',
    'FRIEND_EVENTS': 'friend-events',
    'MESSENGER_EVENTS': 'messenger-events',
    'NEWSFEED_EVENTS': 'newsfeed-events',
    'PAGE_EVENTS': 'page-events',
    'POST_EVENTS': 'post-events',
    'REACTION_EVENTS': 'reaction-events',
    'STORIES_EVENTS': 'stories-events',
    'TAGGING_EVENTS': 'tagging-events',
}

# Authentication Backends
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',  # Default backend for email and password
    'social_core.backends.google.GoogleOAuth2',  # Example: Add Google OAuth2
    'social_core.backends.facebook.FacebookOAuth2',  # Example: Add Facebook OAuth2
]

# Utility function to check if tests are currently running
def is_running_tests():
    return 'test' in sys.argv

# Installed applications, including Django apps, third-party apps, and custom apps
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
    'django_elasticsearch_dsl',

    # Custom apps
    'users.apps.UsersConfig',
    'follows.apps.FollowsConfig',
    'reactions.apps.ReactionsConfig',
    'stories.apps.StoriesConfig',
    'social.apps.SocialConfig',
    'messenger.apps.MessengerConfig',
    'newsfeed.apps.NewsfeedConfig',
    'pages.apps.PagesConfig',
    'tagging.apps.TaggingConfig',
    'friends.apps.FriendsConfig',
    'comments.apps.CommentsConfig',
    'notifications.apps.NotificationsConfig',
    'albums.apps.AlbumsConfig',
    'core.apps.CoreConfig',

    # Kafka broker
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
        'APP_DIRS': True,  # Include app directories for template lookup
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

# WSGI and ASGI applications for handling HTTP and WebSocket requests
WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

# Channels configuration for WebSocket handling
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [(env('REDIS_HOST'), env('REDIS_PORT'))],
        },
    },
}

# Database configuration using PostgreSQL, with credentials loaded from environment variables
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
        },
    },
}

# Password validation settings
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization settings
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
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
    'DEFAULT_AUTHENTICATION_CLASSES': ('rest_framework_simplejwt.authentication.JWTAuthentication',),
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

# Simple JWT configuration
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

# Spectacular configuration
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

# CORS settings
CORS_ALLOWED_ORIGINS = env.list('CORS_ALLOWED_ORIGINS', default=[])

# Email configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = env('EMAIL_HOST')
EMAIL_PORT = env('EMAIL_PORT')
EMAIL_USE_TLS = env('EMAIL_USE_TLS')
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')

# Celery configuration
CELERY_BROKER_URL = env('CELERY_BROKER_URL', default=f'redis://{env("REDIS_HOST")}:{env("REDIS_PORT")}/0')
CELERY_RESULT_BACKEND = env('CELERY_RESULT_BACKEND', default=f'redis://{env("REDIS_HOST")}:{env("REDIS_PORT")}/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'

# Celery Beat Schedule
CELERY_BEAT_SCHEDULE = {
    'consume-user-events-every-5-seconds': {
        'task': 'kafka_app.tasks.consume_user_events',
        'schedule': 5.0,  # every 5 seconds
    },
    'consume-album-events-every-10-seconds': {
        'task': 'albums.tasks.consume_album_events',
        'schedule': 10.0,  # every 10 seconds
    },
    'consume-comment-events-every-10-seconds': {
        'task': 'comments.tasks.consume_comment_events',
        'schedule': 10.0,  # every 10 seconds
    },
    'consume-follow-events-every-10-seconds': {
        'task': 'follows.tasks.consume_follow_events',
        'schedule': 10.0,  # every 10 seconds
    },
    'consume-friend-events-every-10-seconds': {
        'task': 'friends.tasks.consume_friend_events',
        'schedule': 10.0,  # every 10 seconds
    },
    'consume-messenger-events-every-10-seconds': {
        'task': 'messenger.tasks.consume_messenger_events',
        'schedule': 10.0,  # every 10 seconds
    },
    'consume-newsfeed-events-every-10-seconds': {
        'task': 'newsfeed.tasks.consume_newsfeed_events',
        'schedule': 10.0,  # every 10 seconds
    },
    'consume-page-events-every-10-seconds': {
        'task': 'pages.tasks.consume_page_events',
        'schedule': 10.0,  # every 10 seconds
    },
    'consume-reaction-events-every-10-seconds': {
        'task': 'reactions.tasks.consume_reaction_events',
        'schedule': 10.0,  # every 10 seconds
    },
    'consume-social-events-every-10-seconds': {
        'task': 'social.tasks.consume_social_events',
        'schedule': 10.0,  # every 10 seconds
    },
    'consume-stories-events-every-10-seconds': {
        'task': 'stories.tasks.consume_stories_events',
        'schedule': 10.0,  # every 10 seconds
    },
    'consume-tagging-events-every-10-seconds': {
        'task': 'tagging.tasks.consume_tagging_events',
        'schedule': 10.0,  # every 10 seconds
    },
    'consume-notifications-events-every-10-seconds': {
        'task': 'notifications.tasks.consume_notifications_events',
        'schedule': 10.0,  # every 10 seconds
    },
}

# Caching configuration
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': f'redis://{env("REDIS_HOST")}:{env("REDIS_PORT")}/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Sentry integration
SENTRY_DSN = env('SENTRY_DSN', default='')
if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()],
        traces_sample_rate=1.0,
        send_default_pii=True
    )

# CSP settings
CSP_DEFAULT_SRC = ("'none'",)
CSP_SCRIPT_SRC = ("'self'", 'https://apis.google.com', 'https://cdn.jsdelivr.net', "'unsafe-inline'")
CSP_IMG_SRC = ("'self'", 'https://images.unsplash.com', 'https://cdn.jsdelivr.net', 'data:')
CSP_STYLE_SRC = ("'self'", 'https://fonts.googleapis.com', 'https://cdn.jsdelivr.net', "'unsafe-inline'")
CSP_FONT_SRC = ("'self'", 'https://fonts.gstatic.com')
CSP_CONNECT_SRC = ("'self'",)
CSP_BASE_URI = ("'self'",)
CSP_FORM_ACTION = ("'self'",)
CSP_REPORT_URI = '/csp-violation-report/'

# Security settings for production
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
