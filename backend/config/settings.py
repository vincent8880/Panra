"""
Django settings for prediction market platform.
"""

from pathlib import Path
import os
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Helper function to get frontend URL for settings (avoid circular import)
def _get_frontend_url_for_settings():
    """Helper to get frontend URL for settings."""
    frontend = config('FRONTEND_URL', default=None)
    if frontend and frontend != 'http://localhost:3000':
        return frontend
    if os.getenv('RAILWAY_ENVIRONMENT') or os.getenv('RAILWAY_PROJECT_ID'):
        return 'https://panra-ke.up.railway.app'
    return frontend or 'http://localhost:3000'


# Quick-start development settings - unsuitable for production
SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-this-in-production')
DEBUG = config('DEBUG', default=True, cast=bool)

# Allow Railway and other production hosts
ALLOWED_HOSTS = config(
    'ALLOWED_HOSTS',
    default='localhost,127.0.0.1',
    cast=lambda v: [s.strip() for s in v.split(',')]
)

# Automatically allow Railway domains if we're on Railway
import os
if os.getenv('RAILWAY_ENVIRONMENT') or os.getenv('RAILWAY_PROJECT_ID'):
    # We're on Railway - allow all hosts (Railway handles routing/security)
    ALLOWED_HOSTS = ['*']


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',  # Required for allauth
    
    # Third party
    'rest_framework',
    'corsheaders',
    'django_filters',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    
    # Local apps
    'markets',
    'users',
    'trading',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Serve static files
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'allauth.account.middleware.AccountMiddleware',  # Required for allauth
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # Custom templates directory
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'config.context_processors.frontend_url',  # Add FRONTEND_URL to templates
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# Use PostgreSQL if DATABASE_URL is set (Railway provides this), otherwise SQLite for local dev
DATABASE_URL = config('DATABASE_URL', default=None)

if DATABASE_URL:
    # Parse Railway's DATABASE_URL format: postgresql://user:password@host:port/dbname
    import dj_database_url
    DATABASES = {
        'default': dj_database_url.config(default=DATABASE_URL, conn_max_age=600)
    }
else:
    # Local development - use SQLite
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Nairobi'
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# WhiteNoise for serving static files in production
# Use non-compressed storage to avoid issues with redirect responses
STATICFILES_STORAGE = 'whitenoise.storage.ManifestStaticFilesStorage'

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom User Model
AUTH_USER_MODEL = 'users.User'

# Django Allauth Configuration
SITE_ID = 1

# Authentication backends
AUTHENTICATION_BACKENDS = [
    'users.backends.EmailOrUsernameBackend',  # Custom: supports email/username login
    'django.contrib.auth.backends.ModelBackend',  # Default Django auth (fallback)
    'allauth.account.auth_backends.AuthenticationBackend',  # Allauth
]

# Allauth settings
# New recommended settings (replaces deprecated ACCOUNT_EMAIL_REQUIRED, ACCOUNT_USERNAME_REQUIRED, ACCOUNT_AUTHENTICATION_METHOD)
ACCOUNT_LOGIN_METHODS = {'email', 'username'}  # Allow login with email or username
ACCOUNT_SIGNUP_FIELDS = ['email', 'username*', 'password1*', 'password2*']  # Username required (*), email optional
ACCOUNT_EMAIL_VERIFICATION = 'none'  # Disable email verification for now
SOCIALACCOUNT_EMAIL_VERIFICATION = 'none'
SOCIALACCOUNT_AUTO_SIGNUP = True
SOCIALACCOUNT_QUERY_EMAIL = True

# Google OAuth settings
# Note: django-allauth requires SocialApp to be created in database
# Run: python manage.py setup_google_oauth after setting env vars
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        },
    }
}

# Custom allauth adapters
ACCOUNT_ADAPTER = 'users.adapters.CustomAccountAdapter'
SOCIALACCOUNT_ADAPTER = 'users.adapters.CustomSocialAccountAdapter'

# Redirect URL after social login (will redirect to frontend)
# Note: This is a fallback - the adapters handle the actual redirect
LOGIN_REDIRECT_URL = _get_frontend_url_for_settings()
LOGOUT_REDIRECT_URL = _get_frontend_url_for_settings()
SOCIALACCOUNT_LOGIN_ON_GET = True  # Allow GET requests for OAuth

# Force HTTPS in allauth-generated URLs on Railway
if os.getenv('RAILWAY_ENVIRONMENT') or os.getenv('RAILWAY_PROJECT_ID'):
    ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'https'

# REST Framework
# Try to use simplejwt, fallback to session auth if not installed
# Check if simplejwt is available without importing (avoids AppRegistryNotReady error)
try:
    import importlib
    importlib.import_module('rest_framework_simplejwt')
    DEFAULT_AUTH_CLASSES = [
        'rest_framework_simplejwt.authentication.JWTAuthentication',  # JWT token-based auth
        'rest_framework.authentication.SessionAuthentication',  # Session auth (for email/password)
    ]
except ImportError:
    # Fallback during deployment before package is installed
    DEFAULT_AUTH_CLASSES = [
        'rest_framework.authentication.SessionAuthentication',  # Session auth only
    ]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': DEFAULT_AUTH_CLASSES,
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# SimpleJWT Configuration (only if package is installed)
try:
    from datetime import timedelta
    SIMPLE_JWT = {
        'ACCESS_TOKEN_LIFETIME': timedelta(days=7),  # Access token valid for 7 days
        'REFRESH_TOKEN_LIFETIME': timedelta(days=30),  # Refresh token valid for 30 days
        'ROTATE_REFRESH_TOKENS': True,  # Generate new refresh token on each refresh
        'BLACKLIST_AFTER_ROTATION': True,  # Blacklist old refresh tokens
        'ALGORITHM': 'HS256',
        'SIGNING_KEY': SECRET_KEY,
        'AUTH_HEADER_TYPES': ('Bearer',),
        'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
        'USER_ID_FIELD': 'id',
        'USER_ID_CLAIM': 'user_id',
    }
except ImportError:
    # Package not installed yet, will be available after pip install
    pass

# CORS settings
# Allow frontend origin from environment variable (Railway will set this)
FRONTEND_URL = _get_frontend_url_for_settings()
CORS_ALLOWED_ORIGINS = config(
    'CORS_ALLOWED_ORIGINS',
    default=f'{FRONTEND_URL},http://localhost:3000,http://127.0.0.1:3000',
    cast=lambda v: [s.strip() for s in v.split(',')]
)

# Critical for cross-domain authentication
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# CSRF trusted origins for Railway domains
CSRF_TRUSTED_ORIGINS = config(
    'CSRF_TRUSTED_ORIGINS',
    default=f'{FRONTEND_URL},http://localhost:3000,http://127.0.0.1:3000',
    cast=lambda v: [s.strip() for s in v.split(',')]
)

# Automatically allow Railway domains for CSRF
if os.getenv('RAILWAY_ENVIRONMENT') or os.getenv('RAILWAY_PROJECT_ID'):
    # Add Railway backend domain to trusted origins
    railway_domain = f"https://{os.getenv('RAILWAY_STATIC_URL', 'panra.up.railway.app')}"
    if railway_domain not in CSRF_TRUSTED_ORIGINS:
        CSRF_TRUSTED_ORIGINS.append(railway_domain)
    
    # Add frontend domain to CSRF trusted origins (use helper function)
    frontend_url = _get_frontend_url_for_settings()
    if frontend_url and frontend_url not in CSRF_TRUSTED_ORIGINS:
        CSRF_TRUSTED_ORIGINS.append(frontend_url)
    
    # Add frontend to CORS if not already there
    if frontend_url and frontend_url not in CORS_ALLOWED_ORIGINS:
        CORS_ALLOWED_ORIGINS.append(frontend_url)
    
    # Force HTTPS detection behind Railway proxy (for OAuth redirects)
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Session and cookie settings
SESSION_COOKIE_AGE = 86400 * 7  # 7 days
SESSION_COOKIE_HTTPONLY = True
SESSION_SAVE_EVERY_REQUEST = True  # Refresh session on each request

# For cross-domain authentication (backend and frontend on different domains)
# We need SameSite=None with Secure=True
if os.getenv('RAILWAY_ENVIRONMENT') or os.getenv('RAILWAY_PROJECT_ID'):
    # Production: Different domains require SameSite=None
    SESSION_COOKIE_SAMESITE = 'None'
    SESSION_COOKIE_SECURE = True
    # Don't set SESSION_COOKIE_DOMAIN - let it default to backend domain
    # Frontend will receive cookie via CORS with credentials
else:
    # Development: Same origin or localhost
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = False

# CSRF cookie settings
CSRF_COOKIE_HTTPONLY = False  # Allow JavaScript to read CSRF token
if os.getenv('RAILWAY_ENVIRONMENT') or os.getenv('RAILWAY_PROJECT_ID'):
    CSRF_COOKIE_SAMESITE = 'None'
    CSRF_COOKIE_SECURE = True
else:
    CSRF_COOKIE_SAMESITE = 'Lax'
    CSRF_COOKIE_SECURE = False
CSRF_USE_SESSIONS = False  # Use cookie-based CSRF tokens

# Security settings for production
if not DEBUG:
    SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=False, cast=bool)
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'users': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'allauth': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

