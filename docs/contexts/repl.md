# REPL

## shell

Traditionally, one would use the terminal to enter the shell:

```sh
python manage.py shell
# Python 3.11.3 (main) [Clang 14.0.3 (clang-1403.0.22.14.1)]
# Type 'copyright', 'credits' or 'license' for more information
# IPython 8.13.2 -- An enhanced Interactive Python. Type '?' for help.
#
In [1]:
```

## shell_plus

Since I'd like to load Django models, django-extensions [shell_plus](https://django-extensions.readthedocs.io/en/latest/shell_plus.html) does this automatically:

  ```sh
  python manage.py shell_plus
  # # Shell Plus Model Imports
  # from allauth.account.models import EmailAddress, EmailConfirmation
  # from allauth.socialaccount.models import SocialAccount, SocialApp, SocialToken
  # from django.contrib.admin.models import LogEntry
  # from django.contrib.auth.models import Group, Permission
  # from django.contrib.contenttypes.models import ContentType
  # from django.contrib.sessions.models import Session
  # from django.contrib.sites.models import Site
  # from pages.models import Agreement, UserConsent
  # from profiles.models import Profile, User
  # # Shell Plus Django Imports
  # from django.core.cache import cache
  # from django.conf import settings
  # from django.contrib.auth import get_user_model
  # from django.db import transaction
  # from django.db.models import Avg, Case, Count, F, Max, Min, Prefetch, Q, Sum, When
  # from django.utils import timezone
  # from django.urls import reverse
  # from django.db.models import Exists, OuterRef, Subquery
  # Python 3.11.3 (main) [Clang 14.0.3 (clang-1403.0.22.14.1)]
  # Type 'copyright', 'credits' or 'license' for more information
  # IPython 8.13.2 -- An enhanced Interactive Python. Type '?' for help.
  In [1]:
  ```

## IDE

Nowadays I like using vscode's Jupyter [extension](https://marketplace.visualstudio.com/items?itemName=ms-toolsai.jupyter)
to enter this context. But this requires the running of an initial script:

```py title="Without initialization, running code in jupyter results in error"
>>> from django.conf import settings
>>> settings
...
ImproperlyConfigured: Requested settings, but settings are not configured.

You must either define the environment variable DJANGO_SETTINGS_MODULE or call settings.configure() before accessing settings.
```

Let's fix that error message by running this script prior to Django-related cells:

```py title="Run this cell first"
import os
import sys
import django
from dotenv import load_dotenv
from pathlib import Path

BASE_DIR = Path().cwd() # 1
sys.path.insert(0, BASE_DIR)
load_dotenv(".env", override=True)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings") # (2)
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true" # (3)
django.setup() # (4)
```

1. Note this might need to change depending on location: BASE_DIR = Path(__file__).parent.parent
2. Access django imports
3. Allow qs async filtering in a cell
4. This is for setting up django

This script adds the project base directory to the `sys.path`, enabling detection of module imports. Assumes local `.env` exists in a project called `config`.

In subsequent cells, can access various Django objects:

```py title="Can now run this in the subsequent cell"
>>> from django.conf import settings
>>> settings
<LazySettings "config.settings">
>>> settings.ROOT_URLCONF
'config.urls'
```
