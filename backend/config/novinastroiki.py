import os
import sys
from pathlib import Path
from datetime import timedelta
import environ
from django.conf import settings
from core.management.commands.migration_questioner import \
    NonInteractiveMigrationQuestioner

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

# Initialize environment variables using django-environ
env = environ.Env(
    # Define default types and default values for environment variables
    DEBUG=(bool, False),
    DJANGO_SECRET_KEY=(str, 'your-default-secret-key'),
    ALLOWED_HOSTS=(list, ['localhost', '127.0.0.1']),
    POSTGRES_DB=(str, 'app_db'),
    POSTGRES_USER=(str, 'app_user'),
    POSTGRES_PASSWORD=(str, 'app_password'),
    DB_HOST=(str, 'db'),
    DB_PORT=(str, '5432'),
    CORS_ALLOWED_ORIGINS=(list, ['http://localhost:3000', 'http://127.0.0.1:3000']),
)

# Load environment variables from the .env file located in the project base directory
environ.Env.read_env(
    env_file=os.path.join(Path(__file__).resolve().parent.parent, '.env')
)

# Set the base directory for the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Secret key used for cryptographic signing
SECRET_KEY = env('DJANGO_SECRET_KEY')

# Debug mode, should be set to False in production
DEBUG = env('DEBUG')

# List of allowed hosts that can make requests to this Django instance
ALLOWED_HOSTS = env('ALLOWED_HOSTS')


# Utility function to check if tests are currently running
def is_running_tests():
    return 'test' in sys.argv


# Installed applications, including Django apps, third-party apps, and custom apps
INSTALLED_APPS = [
    'django.contrib.admin',  # Django admin interface
    'django.contrib.auth',  # Authentication framework
    'django.contrib.contenttypes',  # Content types framework
    'django.contrib.sessions',  # Session management
    'django.contrib.messages',  # Messaging framework
    'django.contrib.staticfiles',  # Static files management
    'rest_framework',  # Django REST Framework for building APIs
    'rest_framework_simplejwt.token_blacklist',
    # Token blacklist app for JWT authentication
    'djoser',  # REST implementation of Django authentication
    'corsheaders',  # Cross-Origin Resource Sharing support
    'channels',  # Django Channels for WebSockets
    'django_extensions',  # Additional Django management commands
    'drf_spectacular',  # OpenAPI schema generation
    'users.apps.UsersConfig',  # Custom user app
    'follows.apps.FollowsConfig',  # Follow system app
    'reactions.apps.ReactionsConfig',  # Reaction system app
    'stories.apps.StoriesConfig',  # Stories feature app
    'social.apps.SocialConfig',  # Social networking app
    'messenger.apps.MessengerConfig',  # Messaging app
    'newsfeed.apps.NewsfeedConfig',  # Newsfeed app
    'pages.apps.PagesConfig',  # Pages app
    'tagging.apps.TaggingConfig',  # Tagging app
    'friends.apps.FriendsConfig',  # Friends system app
    'comments.apps.CommentsConfig',  # Commenting system app
    'notifications.apps.NotificationsConfig',  # Notifications app
    'albums.apps.AlbumsConfig',  # Albums feature app
    'core.apps.CoreConfig',
    'django_celery_beat',  # Schedule Periodic Tasks
    'csp',
]

# Middleware configuration
MIDDLEWARE = [
    'csp.middleware.CSPMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # Handles CORS headers for API
    'django.middleware.security.SecurityMiddleware',  # Security-related middleware
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Serve static files in production
    'django.contrib.sessions.middleware.SessionMiddleware',
    # Session management middleware
    'django.middleware.common.CommonMiddleware',  # Common HTTP request processing
    'django.middleware.csrf.CsrfViewMiddleware',  # CSRF protection middleware
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    # Authentication middleware
    'django.contrib.messages.middleware.MessageMiddleware',
    # Messaging framework middleware
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # Clickjacking protection middleware
]

# Root URL configuration
ROOT_URLCONF = 'config.urls'

# Template engine configuration
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # Django's template engine
        'DIRS': [],  # List of directories to search for templates
        'APP_DIRS': True,  # Include app directories for template lookup
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                # Adds debug context processor
                'django.template.context_processors.request',
                # Adds request context processor
                'django.contrib.auth.context_processors.auth',
                # Adds authentication context processor
                'django.contrib.messages.context_processors.messages',
                # Adds messages context processor
            ],
        },
    },
]

# WSGI and ASGI applications for handling HTTP and WebSocket requests
WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

# Database configuration using PostgreSQL, with credentials loaded from environment
# variables
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',  # PostgreSQL database backend
        'NAME': env('POSTGRES_DB'),  # Database name
        'USER': env('POSTGRES_USER'),  # Database user
        'PASSWORD': env('POSTGRES_PASSWORD'),  # Database password
        'HOST': env('DB_HOST'),  # Database host
        'PORT': env('DB_PORT'),  # Database port
        'CONN_MAX_AGE': 600,  # Optimizing database performance
        'TEST': {
            'NAME': 'test_' + env('POSTGRES_DB'),  # Test database name
        },
    },
    # Remove 'test_db' if not necessary
}

# Password validation settings
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation'
                '.UserAttributeSimilarityValidator',
        # Prevents using similar attributes
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        # Minimum password length
        'OPTIONS': {'min_length': 3},  # Set minimum length to 3 characters
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
        # Prevents using common passwords
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
        # Prevents using only numeric passwords
    },
]

# Internationalization settings
LANGUAGE_CODE = 'en-us'  # Default language code
TIME_ZONE = 'UTC'  # Default time zone
USE_I18N = True  # Enable internationalization
USE_L10N = True  # Enable localization
USE_TZ = True  # Enable timezone support

# Static and media file settings
STATIC_URL = '/static/'  # URL to access static files
MEDIA_URL = '/media/'  # URL to access media files
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')  # Directory for media files
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')  # Directory for static files

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom user model
AUTH_USER_MODEL = 'users.CustomUser'

# Django REST Framework configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        # Use JWT authentication
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    # OpenAPI schema generation
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    # Default pagination
    'PAGE_SIZE': 10,  # Default page size

    # Throttling settings
    'DEFAULT_THROTTLE_CLASSES': (
        'rest_framework.throttling.AnonRateThrottle',  # Throttle anonymous users
        'rest_framework.throttling.UserRateThrottle',  # Throttle authenticated users
    ),
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/day',  # Allow 100 requests per day for anonymous users
        'user': '1000/day',  # Allow 1000 requests per day for authenticated users
        'signup': '10/hour',  # Custom throttle for signup
    }
}

# JWT configuration using Simple JWT
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=5),  # Access token lifetime
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),  # Refresh token lifetime
    'ROTATE_REFRESH_TOKENS': True,  # Rotate refresh tokens
    'BLACKLIST_AFTER_ROTATION': True,  # Blacklist tokens after rotation
    'ALGORITHM': 'HS256',  # Algorithm used for token signing
    'SIGNING_KEY': env('DJANGO_SECRET_KEY'),  # Key used to sign tokens
    'AUTH_HEADER_TYPES': ('Bearer',),  # Type of authentication header
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',  # Name of the authorization header
    'USER_ID_FIELD': 'id',  # Field to use for user identification
    'USER_ID_CLAIM': 'user_id',  # Claim to use for user identification
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    # Type of token to use
    'TOKEN_TYPE_CLAIM': 'token_type',  # Claim to indicate token type
    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    # Claim for sliding token expiration
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),  # Sliding token lifetime
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
    # Sliding token refresh lifetime
}

# Djoser configuration for handling authentication views
DJOSER = {
    'LOGIN_FIELD': 'email',  # Use email as the login field
    'USER_CREATE_PASSWORD_RETYPE': True,  # Require password retype on user creation
    'USERNAME_CHANGED_EMAIL_CONFIRMATION': True,
    # Send email confirmation on username change
    'PASSWORD_CHANGED_EMAIL_CONFIRMATION': True,
    # Send email confirmation on password change
    'SEND_CONFIRMATION_EMAIL': True,  # Send confirmation emails
    'SET_USERNAME_RETYPE': True,  # Require username retype
    'SET_PASSWORD_RETYPE': True,  # Require password retype
    'PASSWORD_RESET_CONFIRM_URL': 'password/reset/confirm/{uid}/{token}',
    # URL for password reset confirmation
    'USERNAME_RESET_CONFIRM_URL': 'email/reset/confirm/{uid}/{token}',
    # URL for username reset confirmation
    'ACTIVATION_URL': 'activate/{uid}/{token}',  # URL for user activation
    'SEND_ACTIVATION_EMAIL': True,  # Send activation email
    'SERIALIZERS': {
        'user_create': 'djoser.serializers.CustomUserSerializer',
        # Serializer for user creation
        'user': 'djoser.serializers.UserSerializer',  # Serializer for user data
        'current_user': 'djoser.serializers.UserSerializer',
        # Serializer for current user
        'user_delete': 'djoser.serializers.UserDeleteSerializer',
        # Serializer for user deletion
    },
}

# Configuration for drf-spectacular (OpenAPI/Swagger generation)
SPECTACULAR_SETTINGS = {
    'TITLE': 'Social NEtwork APIs',  # Title of the API documentation
    'DESCRIPTION': 'Your API description',  # Description of the API
    'VERSION': '1.0.0',  # API version
    'SERVE_INCLUDE_SCHEMA': False,  # Include schema in the documentation
    'SWAGGER_UI_SETTINGS': {
        'docExpansion': 'none',  # Swagger UI settings
        'defaultModelsExpandDepth': -1,  # Depth to expand models
    },
    'COMPONENT_SPLIT_REQUEST': True,  # Split requests into components
    'SECURITY': [
        {
            'BearerAuth': []  # Security scheme for bearer token authentication
        }
    ],
    'SCHEMA_COERCE': {
        'securitySchemes': {
            'BearerAuth': {
                'type': 'http',  # Type of security scheme
                'scheme': 'bearer',  # Scheme type
                'bearerFormat': 'JWT'  # Format for the bearer token
            }
        }
    },
}

# CORS configuration to allow specific origins
CORS_ALLOWED_ORIGINS = env.list('CORS_ALLOWED_ORIGINS', default=[])

# Static files storage settings for production using WhiteNoise
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Email configuration settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'  # Backend to use for sending emails
EMAIL_HOST = 'smtp.gmail.com'  # SMTP host
EMAIL_PORT = 587  # SMTP port
EMAIL_USE_TLS = True  # Use TLS for email
EMAIL_HOST_USER = env('EMAIL_HOST_USER')  # Email host user
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')  # Email host password

# Security settings for production
if not DEBUG:
    SECURE_SSL_REDIRECT = True  # Redirect all HTTP requests to HTTPS
    CSRF_COOKIE_SECURE = True  # Use secure cookies for CSRF
    SESSION_COOKIE_SECURE = True  # Use secure cookies for sessions
    SECURE_BROWSER_XSS_FILTER = True  # Enable browser XSS protection
    SECURE_CONTENT_TYPE_NOSNIFF = True  # Prevent content type sniffing
    X_FRAME_OPTIONS = 'DENY'  # Prevent clickjacking
    SECURE_HSTS_SECONDS = 31536000  # HTTP Strict Transport Security (HSTS) duration
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True  # Include subdomains in HSTS
    SECURE_HSTS_PRELOAD = True  # Preload HSTS
    SECURE_REFERRER_POLICY = 'no-referrer-when-downgrade'  # Referrer policy
    SECURE_PROXY_SSL_HEADER = (
        'HTTP_X_FORWARDED_PROTO', 'https')  # Header for SSL proxy

# Configuration for Django Channels using Redis as the backend
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',  # Redis channel layer
        'CONFIG': {
            'hosts': [('redis', 6379)],  # Redis server configuration
        },
    },
}

# Migration modules configuration for non-interactive migration questioner
MIGRATION_MODULES = {
    "default": {
        "QUESTIONER": NonInteractiveMigrationQuestioner
    }
}

# Internal IPs for Django Debug Toolbar
INTERNAL_IPS = [
    '127.0.0.1',  # Localhost IP
    'localhost',  # Localhost
]

# Django Debug Toolbar configuration
DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': lambda request: settings.DEBUG and not is_running_tests(),
    # Show toolbar in debug mode only
    'INTERCEPT_REDIRECTS': False,  # Don't intercept redirects
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
        'core': {  # Add your app logger
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

# Celery Configuration Options
CELERY_BROKER_URL = 'redis://redis:6379/0'  # Using Redis as the message broker
CELERY_RESULT_BACKEND = 'redis://redis:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'

# Caching Configuration
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://redis:6379/1',
        # redis service name and port from docker-compose
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Sentry - tracking errors and performance issues
sentry_sdk.init(
    dsn=env('SENTRY_DSN'),
    integrations=[DjangoIntegration()],
    traces_sample_rate=1.0,  # Adjust based on need
    send_default_pii=True
)

# CSP settings
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


# Kafka settings
KAFKA_BROKER_URL = 'localhost:9092'

KAFKA_TOPICS = {
    'USER_EVENTS': 'user-events',
    'NOTIFICATIONS': 'user-notifications',
}