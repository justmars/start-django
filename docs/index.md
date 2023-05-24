---
hide:
- toc
---
# :simple-django: start-django Docs

[start-django.fly.dev](https://start-django.fly.dev) :simple-python: `^3.11` :simple-django: `4.2` + :material-airballoon: `fly.io` personal boilerplate, ft.:

1. UI from [django-fragments](https://github.com/justmars/django-fragments) attempting [locality-of-behavior](https://htmx.org/essays/locality-of-behaviour/):
      1. [`{% icon %}`](https://mv3.dev/django-fragments/icon) - `<svg>` tag combiner
      2. [`{% themer %}`](https://mv3.dev/django-fragments/themer) - `<button onclick=toggleTheme()>` enclosing  two `{% icon %}s`.
      3. [`{% hput %}`](https://mv3.dev/django-fragments/hput) - [TailwindCSS](https://tailwindcss.com/) + [widget-tweakable](https://github.com/jazzband/django-widget-tweaks) `<input>`
      4. [`{% sel %}`](https://mv3.dev/django-fragments/architectures/listbox) - [hyperscript](https://hyperscript.org) w/ aria-* `<select>`
      5. [`{% include '_msg.html' ... %}`](https://mv3.dev/django-fragments/architectures/alert) - :simple-django:-[htmx](https://htmx.org) messages
2. Deployable [fly.toml](./deploy/prep.md) based on [compose.yml](./contexts/container.md) `services`:
      1. `web`: :simple-django: toggle [settings](./references/settings.md): _dev_ | _test_ | _prod_
      2. `db`: _sqlite_ default, _postgres_-[configurable](./setup//use-postgres.md)
      3. `worker`:  [huey](./setup/background-tasks.md) background tasks
      4. `redis`: message broker
3. Connected [Custom User Model](https://docs.djangoproject.com/en/dev/topics/auth/customizing/#substituting-a-custom-user-model):
      1. [django-allauth](https://django-allauth.readthedocs.io/en/latest/) logic where UI templates have been styled.
      2. [python-postmark](https://github.com/themartorana/python-postmark/#django) transactional emails (e.g. _confirm auth_, _change password_, etc.)
      3. 1-to-1 [Profile](setup/user-model.md) with  `ImageField` (custom [storage class](https://www.mv3.dev/cloudflare-images#django) to host/serve [Cloudflare Images](https://www.cloudflare.com/products/cloudflare-images/))
      4. foreign key `UserConsent` model for _Terms of Use_.

=== ":material-run-fast: just start"

    ```{ .sh title="poetry, npm, vscode, just, ^3.11 python" .copy}
    # 'just' wraps initial setup into a single command
    gh repo clone justmars/start-django dj \
      && cd dj \
      && just start # (1)
    ```

    1. When copy/pasting, just change `dj` to whatever folder. See :fontawesome-solid-person-walking-luggage: to unpack steps in this [recipe](https://github.com/casey/just) which includes virtual environment (`.venv`) setup via `poetry`; installation of tailwind with `npm` and running the build step with `npx tailwindcss`; and initial :simple-django: management commands: `collectstatic`, `compress`, `makemigrations`, `migrate` and `runserver_plus` (from `django_extensions`).

=== ":fontawesome-solid-person-walking-luggage: unpack"

    ```sh title="Setup using native commmands without 'just'; requires: poetry, npm, python ^3.11" linenums="1"
    gh repo clone justmars/start-django && cd start-django

    cp ./etc/env.example.0.dev .env # (1)
    npm install -D tailwindcss \
      @tailwindcss/typography \
      @tailwindcss/forms \
      @tailwindcss/aspect-ratio \
      @tailwindcss/container-queries # (2)

    npx tailwindcss \
    -i ./src/static/css/input.css \
    -o ./src/static/css/output.css # (3)

    poetry install && \
    poetry export -f requirements.txt \
    --without-hashes \
    --output src/requirements.txt \
    && poetry shell # (4)

    test -d src/data || mkdir src/data
    cd src
    python manage.py makemigrations # (5)
    python manage.py migrate # (6)
    python manage.py collectstatic --noinput # (7)
    python manage.py compress --force # (8)

    pre-commit autoupdate # ensure updated config
    pre-commit run --all-files # applies: ruff, black, djhtml
    pytest # will use pyproject.toml args

    python manage.py runserver_plus # (9)
    ```

    1. Set example file to .env to make it easy to supply [env vars](./references/env-vars.md).
    2. This will create `/nodemodules/` (`.gitignore`ed) containing TailwindCSS dependencies.
    3. Invokes `/src/static/css/input.css` + `./tailwind.config.js` to build `/static/css/output.css`. See full [process](./references/tailwind-setup.md)
    4. Installs virtual environment in a local `.venv` (assumes `poetry config --list` shows `virtualenvs.create = true` and `virtualenvs.in-project = true`) then creates `poetry.lock`, ensures a copy of the requirements.txt file is copied into `/src`
    5. Prepares models declared in `src/pages` and `/src/profiles` as sql statements found in `/migrations` folder of each app. Since I didn't declare a `DATABASE_URL` in the environment, this will default to creating an empty `src/db.sqlite`
    6. Sets up tables in default sqlite database (unless a `DATABASE_URL` pointing to a local postgres db is set in `.env`)
    7. Populates `/src/staticfiles` directory
    8.  Creates compressed css / js manifest in `/src/static/CACHE`
    9.  Django management command to launch django.setup(). No need to setup `.env` values since default local settings will be used as a quickstart example. Uses django_extention's [runserver_plus](https://django-extensions.readthedocs.io/en/latest/runserver_plus.html)

!!! tip "Details"

    After initial setup:

    1. [Personalize installation](./references/personalization.md)
    2. [Setup services](./setup/summary.md)
    3. [Review settings](./)
    4. [Evaluate design](./design.md)
    5. [Consider contexts](./contexts/overview.md)[^1], e.g. [containers](./contexts/container.md)
    6. [Deploy site](./deploy/prep.md)
