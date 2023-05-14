from environs import EnvError

from ._settings import *  # core settings

AUTH_USER_MODEL = "profiles.User"  #  overriden;
AUTHENTICATION_BACKENDS = [
    "allauth.account.auth_backends.AuthenticationBackend",  # required: allauth
    "django.contrib.auth.backends.ModelBackend",  # default
]
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
        )
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Email-Related Settings

"""Email prerequisites"""
_email = "do@configure.separately"
EMAIL_RECIPIENT = env("EMAIL_RECIPIENT", _email)
EMAIL_SENDER = env("EMAIL_SENDER", _email)
EMAIL_NOT_CONFIGURED = None
if not all([_email != EMAIL_RECIPIENT, _email != EMAIL_SENDER]):
    EMAIL_NOT_CONFIGURED = f"{EMAIL_SENDER=} and {EMAIL_RECIPIENT=} must be configured."

""" Postmark for Transacational Emails"""
POSTMARK_API_KEY = env("POSTMARK_API_KEY", None)
POSTMARK_SENDER = EMAIL_SENDER
POSTMARK_TEST_MODE = False
POSTMARK_TRACK_OPENS = True
POSTMARK_RETURN_MESSAGE_ID = True
DEFAULT_FROM_EMAIL = EMAIL_SENDER

# Authentication Settings, see https://django-allauth.readthedocs.io/en/latest/advanced.html#custom-user-models

"""Adapters to change the revised signup flow: consent + profile"""
ACCOUNT_ADAPTER = "profiles.adapters.ConsentBasicAdapter"
SOCIALACCOUNT_ADAPTER = "profiles.adapters.ConsentSocialAdapter"

"""Forms to handle revised login flow: consent + profile"""
ACCOUNT_FORMS = {"signup": "profiles.forms.ConsentBasicForm"}
SOCIALACCOUNT_FORMS = {"signup": "profiles.forms.ConsentSocialForm"}

"""Authentication will be by email vs. username"""
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_EMAIL_VERIFICATION = "mandatory"

"""Authentication protocol"""
ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = False
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 1
ACCOUNT_EMAIL_SUBJECT_PREFIX = ""
ACCOUNT_LOGIN_ATTEMPTS_TIMEOUT = 86400
ACCOUNT_LOGIN_ATTEMPTS_LIMIT = 5
ACCOUNT_LOGOUT_ON_GET = True
ACCOUNT_EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL = "account_email"
LOGIN_REDIRECT_URL = "profiles:settings"

"""Social authentication protocol"""
SOCIALACCOUNT_EMAIL_VERIFICATION = "none"
SOCIALACCOUNT_AUTO_SIGNUP = False
SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "APP": {
            "client_id": env("GOOGLE_ID", None),
            "secret": env("GOOGLE_KEY", None),
        }
    },
    "github": {
        "APP": {
            "client_id": env("GITHUB_ID", None),
            "secret": env("GITHUB_KEY", None),
            "key": "",
        }
    },
}


def check_auth():
    if SOCIALACCOUNT_PROVIDERS.get("google"):
        if not env("GOOGLE_ID", None) or not env("GOOGLE_KEY", None):
            raise EnvError("Please set Google ID+KEY oAuth.")
    if SOCIALACCOUNT_PROVIDERS.get("github"):
        if not env("GITHUB_ID", None) or not env("GITHUB_KEY", None):
            raise EnvError("Please set Github ID+KEY oAuth.")
    if POSTMARK_API_KEY:
        if EMAIL_NOT_CONFIGURED:
            raise EnvError(EMAIL_NOT_CONFIGURED)


"""
    "facebook": {
        "APP": {
            "client_id": env("FB_ID", None),
            "secret": env("FB_KEY", None),
            "key": "",
        },
        "METHOD": "js_sdk",
        "SCOPE": ["email", "public_profile"],
        "AUTH_PARAMS": {"auth_type": "reauthenticate"},
        "INIT_PARAMS": {"cookie": True},
        "FIELDS": [
            "id",
            "first_name",
            "last_name",
            "middle_name",
            "name",
            "name_format",
            "picture",
            "short_name",
        ],
        "EXCHANGE_TOKEN": True,
        "VERIFIED_EMAIL": False,
        "VERSION": "v16.0",
        "GRAPH_API_URL": "https://graph.facebook.com/v16.0",
    },
    """
