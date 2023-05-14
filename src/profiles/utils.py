import re

from django.conf import settings
from django.core.files.storage import storages  # type: ignore

regex = r"(?P<prefix_url>.*)(?=\=.*$)"
pattern = re.compile(regex)
"""
Matches text without the trailing = suffix so that this can be replaced

e.g. https://lh3.googleusercontent.com/a/gibberish-text=s96-c

will return https://lh3.googleusercontent.com/a/gibberish-text
"""


def set_base_img_url(url: str):
    """Get full-sized image from social url instead of reduced version."""
    if "googleusercontent.com" in url:
        if match := pattern.search(url):
            return match.group("prefix_url")
    return url


def select_storage():
    """See https://docs.djangoproject.com/en/dev/topics/files/#using-a-callable"""
    if settings.ENV_NAME == "dev":
        return storages["default"]
    return storages["cloudflare_images"]
