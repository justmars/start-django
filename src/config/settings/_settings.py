import warnings
from pathlib import Path

from django.utils.deprecation import (
    RemovedInDjango50Warning,  # type: ignore
    RemovedInDjango51Warning,  # type: ignore
)
from environs import Env

env = Env()
env.read_env()
# GENERIC
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Manila"  # modified
USE_I18N = True
USE_TZ = True
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# CORE
INSTALLED_APPS = [
    # base
    "django.contrib.admin",  # default
    "django.contrib.auth",  # default
    "django.contrib.contenttypes",  # default
    "django.contrib.sessions",  # default
    "django.contrib.messages",  # default
    "django.contrib.staticfiles",  # needed by debug_toolbar, etc.
    "django.contrib.sites",  # required by allauth
    "django.contrib.sitemaps",  # added for seo
    # auth
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.github",
    "allauth.socialaccount.providers.google",
    "allauth.socialaccount.providers.facebook",
    # third-party
    "huey.contrib.djhuey",  # background tasks
    "widget_tweaks",  # form widgets
    "compressor",  # makes static files like js / css smaller
    "django_extensions",  # general toolkit
    "debug_toolbar",  # debug toolkit
    # custom
    "django_fragments",  # templatetags
    "pages",  # home, about, contact, start templatetags, etc.
    "profiles",  # user settings
]
SITE_ID = 1  # required: allauth
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # added
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",  # added
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
ROOT_URLCONF = "config.urls"  # added
WSGI_APPLICATION = "config.wsgi.application"


# SECURITY
BASE_HOSTS = "0.0.0.0,127.0.0.1,.localhost,testserver"
ALLOWED_HOSTS = env("DJANGO_ALLOWED_HOSTS", BASE_HOSTS).split(",")


# DATABASE
def add_postgres_or_sqlite(setting: dict) -> dict:
    """Accepts the connection string's data dictionary from `dj_database_url`."""
    if name := setting.get("NAME"):
        if name.endswith(".db") or name.endswith(".sqlite"):
            return setting | {"ENGINE": "django.db.backends.sqlite3"}
    return setting | {
        "ENGINE": "django.db.backends.postgresql",
        "OPTIONS": {"connect_timeout": 5},
    }


DATABASES = {
    "default": add_postgres_or_sqlite(
        env.dj_db_url("DATABASE_URL", "sqlite:///data/start.sqlite")
    )
}

# STORAGES
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",  # default
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",  # default
    "compressor.finders.CompressorFinder",  # compressor-added
]
STATICFILES_DIRS = [str(BASE_DIR / "static")]

# See https://docs.djangoproject.com/en/dev/ref/settings/#std-setting-STATICFILES_DIRS
STORAGES = {  # django 4.2 and above
    "default": {  # default
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": (
        {  # default is "django.contrib.staticfiles.storage.StaticFilesStorage"
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        }
    ),
    "cloudflare_images": {  # added via cloudflare_images
        "BACKEND": "cloudflare_images.django.LimitedStorageCloudflareImages",
    },
}
MEDIA_ROOT = BASE_DIR / "mediafiles"  # see STORAGES['default']
STATIC_ROOT = BASE_DIR / "staticfiles"  # see STORAGES['staticfiles']
"""`python manage.py collectstatic --noinput` gathers all static files into this folder """

COMPRESS_ENABLED = True
COMPRESS_ROOT = BASE_DIR / "static"
"""`python manage.py compress --force` creates `/src/static/CACHE/css` and `/src/static/CACHE/js` folders."""

MEDIA_URL = "media/"  # templates {% get_media_prefix %}; provides url prefix
STATIC_URL = "static/"  # templates {% load static %}; provides url prefix

# TEMPLATES
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],  # added
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
FRAGMENTS = {"icons_prefix": "heroicons", "icons_path": BASE_DIR / "templates" / "svg"}


# BACKGROUND
"""
REDIS_URL is explicit indicator of instance.
Also inferred from `redis_db` (compose.yml).
If redis not available, use memory for testing.
Note when `immediate` is `True`, there is no delay that occurs when the background task is called.
See [rationale](https://huey.readthedocs.io/en/latest/contrib.html#debug-and-synchronous-execution)
"""


def check_redis(host: str, port: int = 6379, db: int = 0) -> dict | None:
    import redis

    """Determine if the server is running"""
    r = redis.Redis(host=host, port=port, db=db)
    try:
        r.ping()
        return {"host": host, "port": port, "db": db}
    except redis.ConnectionError:
        return None


if REDIS_URL := env("REDIS_URL", None):
    HUEY = {"connection": {"url": REDIS_URL}, "immediate": False}
elif conn := check_redis(host="redis_db"):
    HUEY = {"connection": conn, "immediate": False}
else:  # default huey_class = huey.RedisHuey, default immediate = settings.DEBUG
    HUEY = {"huey_class": "huey.MemoryHuey", "immediate": True}


# import sentry_sdk
# from sentry_sdk.integrations.django import DjangoIntegration
"""
sentry_sdk.init(
    dsn="xxx",
    integrations=[DjangoIntegration()],
    traces_sample_rate=1.0,
    send_default_pii=True,
)
"""

# LOGGING: Rich
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {"rich": {"datefmt": "%X"}},
    "handlers": {
        "console": {
            "class": "rich.logging.RichHandler",
            "formatter": "rich",
            "level": "DEBUG",
            "markup": True,
        }
    },
    "loggers": {
        "django": {"handlers": ["console"]},
        "django.db.backends": {"level": "INFO"},
    },
}


def ignore_warnings():
    warnings.simplefilter("default")
    for i in [
        RemovedInDjango50Warning,
        RemovedInDjango51Warning,
        DeprecationWarning,
    ]:
        warnings.filterwarnings("ignore", category=i)
