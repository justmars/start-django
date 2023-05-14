# Local

## Setting up environment with dependencies

There are many python-based packaging / dependency solutions.

The setup instructions of this boilerplate relies on `poetry` as a means of orchestrating the setup.

I've moved from `Pipfile` to plain `requirements.txt` to `pyproject.toml` over the last few years but there doesn't seem to be much consensus on how to finalize dependencies. I settled on `poetry` because I liked the fact that it was an early supporter of `pyproject.toml` but it seems like the way this file should be built, populated, run... is still [very much in contention in the community](https://lwn.net/Articles/924114/).

`poetry` seems like the safe winner here since it's nearing 25k stars on Github but the same could have been said of `pipenv` early on (the latter is now nearing 24k stars).

## Getting it to run and look nice

1. Configure initial [settings](../references/settings.md) to run on local machine
2. Integrate local database, see example with [postgres](../setup/use-postgres.md)
3. Running Tailwind build step when [adjusting UI](../references/tailwind-setup.md)
4. Using social auth callback urls with `127.0.0.1` as the host

## Setting up tests

### Creation

1. I'll often do docstring tests to quickly unit test a function so I can grok it immediately.
2. If this requires a formal `*.test` file, I'll populate the `/src/tests` folder

### Running

Instead of having to write the full options list, can simply run `pytest` on the shell
and it will adopt the configuration declared in pyproject.toml :

!!! tip "pyproject.toml x pytest"

    ```toml title="pyproject.toml"
        [tool.pytest.ini_options]
        minversion = "7.0"
        pythonpath = "src" # (1)
        addopts = "-ra -q --ds=config.settings --doctest-modules --cov" # (2)
        filterwarnings = [
          "ignore::DeprecationWarning", # (3)
          "ignore::django.utils.deprecation.RemovedInDjango51Warning" # (4)
        ]
        testpaths = ["tests"]
    ```

    1. :simple-django: is at `src` so it's as if pytest is running under this context
    2. Note `--ds=config.settings` refers to the use of [pytest-django](https://pytest-django.readthedocs.io/en/latest/configuring_django.html)
    3. Ignore the noise- DeprecationWarning: pkg_resources is deprecated as an API
    4. Ignore the noise-  GET_STORAGE_CLASS_DEPRECATED_MSG

## Configuring shortcuts

### `just start`

Requires: `npm`, `poetry`, `just`

```sh
# (1) setup
cp ./etc/env.example.0.dev-op .env
poetry install
poetry shell
npm install -D tailwindcss \
  @tailwindcss/typography \
  @tailwindcss/forms \
  @tailwindcss/aspect-ratio \
  @tailwindcss/container-queries
npx tailwindcss -i ./src/static/css/input.css -o ./src/static/css/output.css

# (2) just req
poetry export -f requirements.txt \
--without-hashes \
--output src/requirements.txt

# (3) just press
rm -rf ./src/static/CACHE
cd src && python manage.py collectstatic --noinput
cd src && python manage.py compress --force

# (4) just db
cd src && python manage.py makemigrations
cd src && python manage.py migrate

# (5) test then run
pre-commit autoupdate
cd src && pytest
cd src && python manage.py runserver_plus
```

1. Setup .venv, create an .env file model and place it in the root
2. Adds a `requirements.txt` inside `/src` based on `pyproject.toml` dependencies.
3. Runs collection and compression of staticfiles.
4. Populates database for use based on existing models declared in `/pages` and `/profiles`
5. Prep dev environment, sanity check on default boilerplate

### `just tw`

`npx tailwindcss -i ./src/static/css/input.css -o ./src/static/css/output.css --watch`

### `just dumpenv`

Requires: `1password`

`op inject -i ./etc/env.example.0.dev-op -o .env`

### `just run`

`open -a "Brave Browser.app" http://127.0.0.1:8000/ && cd src && python manage.py runserver_plus`

### `just work`

`cd src && python manage.py run_huey`

## Documentation

Explaining functions created in the documentation
