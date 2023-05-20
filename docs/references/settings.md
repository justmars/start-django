# Sensible defaults

## File structure

```yaml title="Root folder"
<root>
├── .github/workflows/main.yml # ci
├── .vscode/ # configures mkdocs, ruff, pytest, etc., file associations
├── etc/ # example env variables
├── src/ # main project folder
    ├── config/ # project named config
        ├── settings/
            ├── __init__.py # switch env: dev | test | prod
            ├── _auth.py # django_allauth, postmark email
            ├── _settings.py # base settings
```

## Default Secrets

=== "local: 127.0.0.1"

    ```py title="/etc/env.example.0.dev"
    ENV_NAME= # If not set, will default to dev
    DJANGO_DEBUG= # If not set, DEBUG will always be False
    REDIS_URL=redis:// # If not set, will use Sqlite.Huey
    DATABASE_URL=postgres://db_usr:pw@localhost:5432/db_pg # Default: /src/data/start.sqlite
    DJANGO_SECRET_KEY= # If not set, will use a randomly generated secret when ENV_NAME is dev
    DJANGO_ALLOWED_HOSTS= # If not set, will always use a fixed list
    EMAIL_RECIPIENT= # If not set, will use default (used in contact form)
    EMAIL_SENDER=  # If not set, will use default (used in by transactional email service postmark)
    DEFAULT_FROM_EMAIL= # If not set, will use default (used in by transactional email service postmark)

    # APIs
    POSTMARK_API_KEY= # If not set, Postmark will not work
    GOOGLE_ID= # If not set, Google oAuth will not work with 127.0.0.1
    GOOGLE_KEY= # If not set, Google oAuth will not work with 127.0.0.1
    GITHUB_ID= # If not set, Github oAuth will not work with 127.0.0.1
    GITHUB_KEY= # If not set, Github oAuth will not work with 127.0.0.1
    CF_ACCT_ID=cloudflare-account # If not set, remote media storage of images will not work
    CF_IMG_TOKEN=cloudflare-secret # If not set, remote media storage of images will not work
    CF_IMG_HASH=cloudflare-hash # If not set, remote media storage of images will not work
    ```

=== "test: 0.0.0.0"

    ```py title="/deploy/env.common.tpl: secret references are expanded via 1Password cli" linenums="1" hl_lines="1"
    # Absent: DATABASE_URL + REDIS_URL; present in compose.yml
    ENV_NAME=test
    DJANGO_SECRET_KEY='testing-key-needed'
    DJANGO_DEBUG=True
    POSTMARK_API_KEY=op://dev/postmark/credential
    DEFAULT_FROM_EMAIL="start-django <donotreply@mv3.dev>"
    EMAIL_RECIPIENT=op://dev/start-django/email/recipient
    EMAIL_SENDER=op://dev/start-django/email/sender
    GOOGLE_ID=op://dev/auth-local/google/id
    GOOGLE_KEY=op://dev/auth-local/google/secret
    GITHUB_ID=op://dev/auth-container/github/id
    GITHUB_KEY=op://dev/auth-container/github/secret
    CF_ACCT_ID=op://dev/cloudflare/acct_id
    CF_IMG_TOKEN=op://dev/cloudflare/images/token
    CF_IMG_HASH=op://dev/cloudflare/images/hash
    ```

=== "fly: <your-site>.fly.dev"
    ```py title="/deploy/env.fly.tpl: secret references are expanded via 1Password cli" linenums="1" hl_lines="1 2 11 12 13 14 21"
    # Note the change of secrets from test re: Google, Github, new url = new tokens
    # Note new REDIS_URL from test
    # Note absence of DATABASE_URL, set independently by fly.io
    DJANGO_SECRET_KEY=op://dev/start-django/django/secret_key
    DJANGO_ALLOWED_HOSTS=op://dev/start-django/django/allowed_hosts

    EMAIL_RECIPIENT=op://dev/start-django/email/recipient
    EMAIL_SENDER=op://dev/start-django/email/sender
    DEFAULT_FROM_EMAIL=op://dev/start-django/email/default

    GOOGLE_ID=op://dev/start-django/google/id
    GOOGLE_KEY=op://dev/start-django/google/secret
    GITHUB_ID=op://dev/start-django/github/id
    GITHUB_KEY=op://dev/start-django/github/secret

    CF_ACCT_ID=op://dev/cloudflare/acct_id
    CF_IMG_TOKEN=op://dev/cloudflare/images/token
    CF_IMG_HASH=op://dev/cloudflare/images/hash

    REDIS_URL=op://dev/fly-redis/credential
    POSTMARK_API_KEY=op://dev/postmark/credential
    ```

## Environment Switcher

This boilerplate's `ENV_NAME` settings (`dev`, `test`, `prod`) is shorthand for _"toggle settings so app behaves like this for state `dev`, etc."_. To be clear on what I mean by `test` and `prod` in a hand-wavvy outline mode:

!!! note "`test`, `prod`"

    === "test"

        I use `test` to denote that `DEBUG=False` and now need to make sure that Django app can function as expected in the real world.

        I'll toggle settings depending on need:

        1. use `gunicorn` or `runserver_plus` instead of runserver
        2. try email service, e.g. from `django.core.mail.backends.console.EmailBackend` to `postmark.django_backend.EmailBackend`
        3. save images from MEDIA_ROOT (`/mediafiles`) in the file system to a remote solution like Cloudflare Images
        4. Ensure social authentication works with `127.0.0.1` / `localhost` or with containerized environments using `0.0.0.0`
        5. Since `DEBUG `here is adjustable and defaults to `False`, need to explicitly state that DEBUG is `True` for staticfiles to be served. See [reference box](https://docs.djangoproject.com/en/dev/howto/static-files/#configuring-static-files)
        6. Compress static files to evaluate footprint in browser

    === "prod"

        7. Host and database is now selected
        8. Considerations of authentication, consent and compliance are introduced
        9. Prevent runtime if missing first & third-party secret
        10. Apply security settings to local context
        11. Ensure `.env` file secrets now stored in more secure location for later reuse
        12. Django now prepared for public use in live deployment

=== "switch"

    ```py title="Base switcher in /settings/__init__.py"
    match ENV_NAME := env("ENV_NAME", "dev").lower():
        case "dev":
            ...
        case "test":
            ...
        case "prod":
            ...
    ```

=== "`dev`"

    ```py title="When ENV_NAME is dev or not set"
    # (1)
    DEBUG = True

    # (2)
    SECRET_KEY = env("DJANGO_SECRET_KEY", get_random_secret_key())

    # (3)
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

    # (4)
    ignore_warnings()
    ```

    1. When not explicitly declared `DEBUG` default is `False`.
    2. Will generate a random key if no environment variable `DJANGO_SECRET_KEY` is detected.
    3. Overrides postmark
    4. Limit text being displayed in the terminal during development.

=== "`test`"

    ```py title="When ENV_NAME is test"
    # (1)
    SECRET_KEY = env("DJANGO_SECRET_KEY")

    # (2)
    if DEBUG := env.bool("DJANGO_DEBUG", False):

        # (3)
        INTERNAL_IPS = ALLOWED_HOSTS

    # (4)
    check_auth()

    # (5)
    EMAIL_BACKEND = "postmark.django_backend.EmailBackend"
    ```

    1. If this `SECRET_KEY` not set, will error out
    2. Enable `DEBUG` even on `ENV_NAME` _test_
    3. Used by _django_debug_toolbar_
    4. Ensures that social authentication and email settings have been changed and/or configured.
    5. Uses an email server for transactional emails

=== "`prod`"

    ```py title="When ENV_NAME is prod"
    # (1)
    SECRET_KEY = env("DJANGO_SECRET_KEY")

    # (2)
    check_auth()

    # (3)
    EMAIL_BACKEND = "postmark.django_backend.EmailBackend"

    # (3)
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
    ```

    1. If this `SECRET_KEY` not set, will error out
    2. Ensures that social authentication and email settings have been changed and/or configured.
    3. Uses an email server for transactional emails
    4. Refer to Django security settings
