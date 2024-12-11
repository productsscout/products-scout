from pathlib import Path
from datetime import timedelta
from decouple import config

# =================================================
# Base Directory
# =================================================
BASE_DIR = Path(__file__).resolve().parent.parent

# =================================================
# Secret Key and Debug Mode
# =================================================
SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)

# =================================================
# Allowed Hosts
# =================================================
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='productsscout.com,www.productsscout.com').split(',')
FRONTEND_URL = config('FRONTEND_URL', default='http://localhost:3000')  # Default to local development URL

# =================================================
# Installed Apps
# =================================================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'rest_framework',
    'rest_framework_simplejwt.token_blacklist',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.microsoft',
    'core',
    'api',
]

# =================================================
# REST Framework Settings
# =================================================
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

# =================================================
# Middleware
# =================================================
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

# =================================================
# URL Configuration
# =================================================
ROOT_URLCONF = 'products_scout.urls'

# =================================================
# Templates
# =================================================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

# =================================================
# WSGI Application
# =================================================
WSGI_APPLICATION = 'products_scout.wsgi.application'

# =================================================
# Database
# =================================================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config('DB_NAME'),  # Name of the database (products_scout_db)
        'USER': config('DB_USER'),  # Database username (admin)
        'PASSWORD': config('DB_PASSWORD'),  # Database password
        'HOST': config('DB_HOST', default='products-scout-db.cfcei68sut7s.eu-north-1.rds.amazonaws.com'),  # RDS Endpoint
        'PORT': config('DB_PORT', default='3306', cast=int),  # Default MySQL port
    }
}

# =================================================
# Password Validators
# =================================================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# =================================================
# Internationalization
# =================================================
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# =================================================
# Static and Media Files
# =================================================
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

STATICFILES_DIRS = [BASE_DIR / "products_scout/static"]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# =================================================
# Authentication
# =================================================
AUTH_USER_MODEL = 'core.User'
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "AUTH_HEADER_TYPES": ("Bearer",),
}

# =================================================
# Allauth Settings
# =================================================
SITE_ID = 1
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
SOCIALACCOUNT_QUERY_EMAIL = True
ACCOUNT_ADAPTER = 'core.adapters.MyAccountAdapter'
SOCIALACCOUNT_ADAPTER = "core.adapters.MySocialAccountAdapter"
SOCIALACCOUNT_AUTO_SIGNUP = True
SOCIALACCOUNT_LOGIN_ON_GET = True

# Redirect URLs
LOGIN_REDIRECT_URL = '/dashboard'
LOGOUT_REDIRECT_URL = '/signin'

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            'client_id': config('GOOGLE_CLIENT_ID'),
            'secret': config('GOOGLE_SECRET'),
        },
        'SCOPE': ['profile', 'email'],
    },
    'microsoft': {
        'APP': {
            'client_id': config('MICROSOFT_CLIENT_ID'),
            'secret': config('MICROSOFT_SECRET'),
        },
        'SCOPE': ['User.Read'],
    },
}

# =================================================
# CORS and CSRF Settings
# =================================================
CORS_ALLOWED_ORIGINS = [
    'https://productsscout.com',
    'https://www.productsscout.com',
]
CSRF_TRUSTED_ORIGINS = [
    'https://productsscout.com',
    'https://www.productsscout.com',
]
CORS_ALLOW_CREDENTIALS = True

CSRF_COOKIE_SECURE = True
CSRF_COOKIE_SAMESITE = 'Strict'
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_SAMESITE = 'Strict'

# =================================================
# Logging
# =================================================
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'errors.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}

SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_SSL_REDIRECT = True

# =================================================
# API Keys
# =================================================
OPENAI_API_KEY = config('OPENAI_API_KEY')
AMAZON_API_KEY = config('AMAZON_API_KEY')
AMAZON_API_HOST = config('AMAZON_API_HOST')

# =================================================
# reCAPTCHA Configuration
# =================================================
RECAPTCHA_SECRET_KEY = config('RECAPTCHA_SECRET_KEY')

# =================================================
# Email Configuration
# =================================================
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST')
EMAIL_PORT = config('EMAIL_PORT', cast=int)
EMAIL_USE_SSL = config('EMAIL_USE_SSL', cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')

# =================================================
# For Smtplib (Direct Email Sending)
# =================================================
SMTP_USERNAME = config('SMTP_USERNAME')
SMTP_PASSWORD = config('SMTP_PASSWORD')
SMTP_SERVER = config('SMTP_SERVER')
SMTP_PORT = config('SMTP_PORT', cast=int)
DEFAULT_FROM_EMAIL = config('SMTP_USERNAME')  # Use no-reply alias as the default

# =================================================
# Email Aliases
# =================================================
EMAIL_NO_REPLY = config('EMAIL_NO_REPLY')
EMAIL_SUPPORT = config('EMAIL_SUPPORT')
