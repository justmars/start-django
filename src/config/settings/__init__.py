from django.core.management.utils import get_random_secret_key
from environs import EnvError

from ._auth import *  # _auth.py also includes the base _settings.py

match ENV_NAME := env("ENV_NAME", "dev").lower():
    case "dev":
        DEBUG = True
        SECRET_KEY = env("DJANGO_SECRET_KEY", get_random_secret_key())
        EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
        ignore_warnings()

    case "test":
        SECRET_KEY = env("DJANGO_SECRET_KEY")  # errors out, if not set
        check_auth()  # errors out if social auth and email check fails
        if DEBUG := env.bool("DJANGO_DEBUG", False):  # overrideable
            INTERNAL_IPS = ALLOWED_HOSTS  # debug-toolbar in staging
        EMAIL_BACKEND = "postmark.django_backend.EmailBackend"

    case "prod":
        SECRET_KEY = env("DJANGO_SECRET_KEY")  # errors out, if not set
        check_auth()  # errors out if social auth and email check fails
        EMAIL_BACKEND = "postmark.django_backend.EmailBackend"
        CSRF_COOKIE_SECURE = True
        SECURE_BROWSER_XSS_FILTER = True
        X_FRAME_OPTIONS = "DENY"
        SECURE_SSL_REDIRECT = True
        SECURE_HSTS_SECONDS = 2592000
        SECURE_HSTS_INCLUDE_SUBDOMAINS = True
        SECURE_HSTS_PRELOAD = True
        SECURE_CONTENT_TYPE_NOSNIFF = True
        SESSION_COOKIE_SECURE = True
        SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    case _:
        raise EnvError(f"Limit {ENV_NAME}: 'dev' | 'test' | 'prod'")
