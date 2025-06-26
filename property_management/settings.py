from datetime import timedelta
from pathlib import Path

import stripe
from decouple import config  # type: ignore[import]

BASE_DIR = Path(__file__).resolve().parent.parent

ENVIRONMENT = config("ENVIRONMENT", "dev")
SECRET_KEY = config("SECRET_KEY", "secret")
DEBUG = config("DEBUG", False)

ALLOWED_HOSTS = config("ALLOWED_HOSTS", "").split(",")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third party apps
    "drf_yasg",
    "corsheaders",
    "rest_framework",
    "djoser",
    "phonenumber_field",
    "django_filters",
    "rest_framework_simplejwt.token_blacklist",
    "django_celery_beat",
    "django_celery_results",
    "djstripe",
    # Built In Apps
    "accounting",
    "authentication",
    "dashboard",
    "property",
    "lease",
    "people",
    "maintenance",
    "core",
    "communication",
    "system_preferences",
    "subscription",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

CSRF_TRUSTED_ORIGINS = config("CSRF_TRUSTED_ORIGINS", "").split(",")

CORS_ALLOW_ALL_ORIGINS = config("CORS_ALLOW_ALL_ORIGINS", False, cast=bool)
CORS_ALLOW_METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE"]

ROOT_URLCONF = "property_management.urls"
AUTH_USER_MODEL = "authentication.User"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
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

WSGI_APPLICATION = "property_management.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("POSTGRES_DB", ""),
        "USER": config("POSTGRES_USER", ""),
        "PASSWORD": config("POSTGRES_PASSWORD", ""),
        "HOST": config("POSTGRES_HOST", ""),
        "PORT": config("POSTGRES_PORT", ""),
    }
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

USE_TZ = True

TENANT_GROUP_NAME = "TENANT"

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static_in_env"]
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = config("EMAIL_HOST", "")
EMAIL_HOST_USER = config("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", "")
EMAIL_PORT = config("EMAIL_PORT", "")
DEFAULT_FROM_EMAIL = "Admin from Property Management System <admin@meganoslabs.com>"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
        "core.permissions.ViewDjangoModelPermissions",
    ],
    "DEFAULT_PAGINATION_CLASS": "core.pagination.StandardPagination",
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=2),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
}

DJOSER = {
    "SERIALIZERS": {
        "user": "authentication.serializers.UserSerializer",
        "current_user": "authentication.serializers.UserSerializer",
    },
}

CELERY_BROKER_URL = config("CELERY_BROKER_URL", "")
CELERY_RESULT_BACKEND = "django-db"
CELERY_RESULT_EXTENDED = True

AWS_ACCESS_KEY_ID = config("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY = config("AWS_SECRET_ACCESS_KEY", "")
AWS_S3_REGION_NAME = config("AWS_S3_REGION_NAME", "")
AWS_STORAGE_BUCKET_NAME = config("AWS_STORAGE_BUCKET_NAME", "")
AWS_S3_ENDPOINT_URL = f"https://{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com"

STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

DJSTRIPE_USE_NATIVE_JSONFIELD = True
DJSTRIPE_FOREIGN_KEY_TO_FIELD = "id"
DJSTRIPE_WEBHOOK_SECRET = config("DJSTRIPE_WEBHOOK_SECRET", "")

STRIPE_SECRET_KEY = config("STRIPE_SECRET_KEY", "")
STRIPE_LIVE_MODE = config("STRIPE_LIVE_MODE", cast=bool, default=False)

if STRIPE_LIVE_MODE:
    STRIPE_LIVE_SECRET_KEY = STRIPE_SECRET_KEY
else:
    STRIPE_TEST_SECRET_KEY = STRIPE_SECRET_KEY

ENABLE_STRIPE_CUSTOMER_CREATE = config("ENABLE_STRIPE_CUSTOMER_CREATE", cast=bool, default=True)

stripe.api_key = STRIPE_SECRET_KEY

DISABLE_S3_DELETE_SIGNAL = False

if ENVIRONMENT == "production":
    SESSION_COOKIE_HTTPONLY = True
    CSRF_COOKIE_HTTPONLY = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 15768000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = True
    SECURE_BROWSER_XSS_FILTER = True
elif ENVIRONMENT == "test":
    DISABLE_S3_DELETE_SIGNAL = True
