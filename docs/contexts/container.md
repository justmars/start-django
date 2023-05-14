# Containers

## Notes

1. Removes the local machine as a factor of code so others can replicate local / repository contexts
2. If there are multiple containers, compose it so that databases and third-party services like background workers are included in this ecosystem of containers, an orchestration
3. Run an orchestration in the local machine but without using its resources

!!! note "Some additional thoughts"

    Re: local/repo context, viewers have to reconstruct the local context by following documentation instructions (that may or may not work). In contrast, a composed orchestration of containers (via a `compose.yml`) encapsulates ostensibly running, interrelated code and its a matter of switching it on or off.

    The repository context deals with reproducing the visual / organizational element of code with no guarantee of reproducability since the underlying local machines may be different. The container context deals with packaging code for more robust means of reproduction for the live site context.

## Post-Setup

By this time, I should already be able to run a web server, employ background tasks, and see how these operate with either postgres or sqlite as the database. These are `services` that are operating in the [local context](./local.md). Since deployment means to transfer my local context to a remote one, how can I be certain that the conditions in the remote context will be fit to run my desired `services`?

The answer is the use of containers which, in essence, makes an exact remote replica of the local context.

Here, I'll implement a local container by moving all relevant files into this single context.

Prior to doing so, ensure Docker is installed and running locally.

## Local files

```yaml title="Project Structure" linenums="1" hl_lines="2 10"
start-django (root)
├── deploy/
    ├── pg/ # postgres
        ├── Dockerfile
    ├── sq/ # sqlite
        ├── Dockerfile
├── docs/
├── src/ # main project folder, where all the relevant files should be found
    ├── .dockerignore # (1)
    ├── scripts/ # common to postgres + sqlite
        ├── run.sh
        ├── web.sh
        ├── worker.sh
    ├── config/ # the settings folder of the project
    ...
├── .env # where variables are declared
```

1. Should exclude all non-essential files presently found inside `/src`, this includes:

    1. `*/.sqlite-*`
    2. `*/.db*`
    3. `staticfiles/`
    4. `mediafiles/`

!!! tip "How this document is structured"

    We'll first try to do things manually to see how `compose.yml` makes this process easier.

!!! note "Where to run commands"

    Based on project structure above, make sure to be in the __`<root>` directory__, i.e. where `start-django` cloned.

## Dockerfiles

There are two Dockerfiles that are preconfigured under `/deploy/pg` and `/deploy/sq`.

=== "sqlite"

    ```Dockerfile title="/deploy/sq/Dockerfile" linenums="1" hl_lines="30"
    # syntax=docker/dockerfile:1.2
    FROM python:3.11-slim-bullseye AS builder
    # setup (1)
    RUN apt update \
      && apt install -y build-essential wget pkg-config \
      && apt clean

    # updated version (2)
    ARG sqlite_year=2023
    ARG sqlite_ver=3410200
    RUN wget https://www.sqlite.org/$sqlite_year/sqlite-autoconf-$sqlite_ver.tar.gz \
      && tar xzf sqlite-autoconf-$sqlite_ver.tar.gz && rm sqlite-autoconf-$sqlite_ver.tar.gz \
      && ./sqlite-autoconf-$sqlite_ver/configure --disable-static --enable-fts5 --enable-json1 CFLAGS="-g -O2 -DSQLITE_ENABLE_JSON1" \
      && make && make install

    # backup (3)
    ARG litestream_ver=0.3.9
    RUN wget https://github.com/benbjohnson/litestream/releases/download/v$litestream_ver/litestream-v$litestream_ver-linux-amd64-static.tar.gz \
      && tar xzf litestream-v$litestream_ver-linux-amd64-static.tar.gz && rm litestream-v$litestream_ver-linux-amd64-static.tar.gz \
      && mv litestream /usr/local/bin

    FROM python:3.11-slim-bullseye
    COPY --from=builder /usr/local/lib/ /usr/local/lib/
    COPY --from=builder /usr/local/bin /usr/local/bin
    ENV PYTHONUNBUFFERED=1 \
        PYTHONDONTWRITEBYTECODE=1 \
        PIP_DISABLE_PIP_VERSION_CHECK=1 \
        LD_LIBRARY_PATH=/usr/local/lib

    # remote folder (4)
    WORKDIR /opt/src

    # local folder to remote folder (5)
    COPY /src .

    # in remote folder, install (6)
    RUN pip install -r requirements.txt

    # make executable (7)
    ARG run_cmd
    RUN chmod +x /opt/src/scripts/worker.sh /opt/src/scripts/$run_cmd
    ```

    1. Prepare packages that will be used to setup `litestream` and compile `sqlite` from source
    2. See latest sqlite [version](https://www.sqlite.org/download.html). Supply the most recent version and relevant extensions to use. At the time of this writing: `3.41.2` with `JSON1` + `FTS5` extensions.
    3. See latest litestream [release](https://github.com/benbjohnson/litestream/releases) - for use as sqlite backup and recovery. Supply the most recent version. At the time of this writing: `0.3.9`
    4. Why `opt/`? See some [context](https://www.baeldung.com/linux/opt-directory).

        Why `/src`? We've placed all relevant files inside this directory, including the `requirements.txt`.
    5. Copies `/src` the the folder of the  _present local build context_ to the container's `WORKDIR` which was just set to `/opt/src`
    6. Presumes that `poetry export -f requirements.txt --without-hashes --output src/requirements.txt` has previously been run from the project's root directory
    7. Makes the two files executable but is not run. Note that the `run_cmd` needs to be filled up either during `compose.yml` or `fly.toml` since this can either be `run.sh` or `web.sh`.

=== "postgres"

    ```Dockerfile title="/deploy/pg/Dockerfile"
    # syntax=docker/dockerfile:1.2
    FROM python:3.11-slim-bullseye
    ENV PYTHONUNBUFFERED=1 \
        PYTHONDONTWRITEBYTECODE=1 \
        PIP_DISABLE_PIP_VERSION_CHECK=1

    # psycopg (1)
    RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*

    # same
    WORKDIR /opt/src
    COPY /src .
    RUN pip install -r requirements.txt

    # make executable (2)
    RUN chmod +x /opt/src/scripts/worker.sh /opt/src/scripts/${run_cmd}
    ```

    1. Needed for `psycopg` to use Postgres
    2. Note that the `run_cmd` needs to be filled up either during `compose.yml` or `fly.toml` since this can either be `run.sh` or `web.sh`.

!!! warning "Entrypoint/CMD"

    The included Dockerfiles _do not_ contain a `CMD` / entrypoint script. To run the containers built by the images, I must add a `--entrypoint` flag or use this in a `compose.yml.tpl`

    Note however that both Dockerfiles make a variable argument executable alongside `worker.sh`.

    I can replace this variable argument with either `run.sh` or `web.sh` depending on the context. So I'll use `run.sh` with the `compose.yml.tpl` for testing inside the container. Then I can use `web.sh` as a build argument with `fly.toml` later during deployment.

## Entrypoints

Dockerfile contain instructions but the ones above do not run anything yet. These will be done by the entrypoint scripts.

=== "worker.sh"

    ```sh title="worker.sh for use in multiple contexts"
    #!/bin/bash
    set -e
    python manage.py migrate
    echo "Run worker."
    python manage.py run_huey # (1)
    ```

    1. The background process worker that will only work if env variables are set.

=== "run.sh local"

    ```sh title="run.sh for use in local machine via Dockerfile"
    #!/bin/bash
    set -e
    python manage.py collectstatic --noinput # (1)
    python manage.py compress --force # (2)
    python manage.py migrate # (3)
    gunicorn config.wsgi:application \ # (4)
        --bind 0.0.0.0:8080 \ # (5)
        --workers=2 \
        --capture-output \
        --enable-stdio-inheritance
    ```

    1. Collect static files into `/opt/src/staticfiles`
    2. Compress content from `/opt/src/staticfiles` into `/static/CACHE`
    3. Ensure all migrations affect the database
    4. Serve on production gunicorn (https://docs.gunicorn.org/en/latest/run.html) vs. `python manage.py runserver`; `config.wsgi:application` refers to the exposed application in Django's `/src/config/wsgi.py`. See Django and [server discussion](../extra/production-server.md)
    5. `0.0.0.0` is included in `config.settings.ALLOWED_HOSTS`; `8080` will be exposed port.

=== "web.sh + fly.toml"

    ```sh title="web.sh for use in fly.toml deployment as a process"
    #!/bin/bash
    set -e
    # (1)
    echo "Static files management."
    python manage.py collectstatic --noinput
    python manage.py compress --force
    python manage.py migrate
    # (2)
    echo "Gunicorn server."
    gunicorn config.wsgi:application \
      --bind 0.0.0.0:"$PORT" \
      --worker-tmp-dir /dev/shm \
      --workers=2 \
      --capture-output \
      --enable-stdio-inheritance
    ```

    1. Note similar setup with `run.sh` with the addition of bound port :${PORT} which maps to fly.toml services internal port, see fly.toml's PORT.

## Dockerfile + Entrypoint

=== "sqlite"

    ```sh title="sqlite Dockerfile + entrypoint" linenums="1" hl_lines="8"
    docker build \
      --tag sq \
      --file ./deploy/sq/Dockerfile \
      --build-arg litestream_ver=0.3.9 \
      --build-arg sqlite_year=2023 \
      --build-arg sqlite_ver=3410200 \
      --build-arg run_cmd=run.sh \
      .
    # why "."? (1)
    # exporting to image ...
    # writing image ...
    # naming to docker.io/library/sq

    docker run --publish 8080:8080 \
      --env-file .env \
      --entrypoint scripts/run.sh \
      --env DATABASE_URL=sqlite:////var/lib/test.sqlite \
      sq
    # Re: 8080: (2), entrypoint (3)
    # Serve app via gunicorn on 8080 (note connection to sqlite:////var/lib/test.sqlite)
    # [<time>][INFO] Starting gunicorn 20.1.0
    # [<time>][INFO] Listening at: http://0.0.0.0:8080
    ```

    1. The Dockerfile referenced contains the following instruction `COPY /src to .`. Since I'm at the root directory in running `docker build` the local context is `.` and I'm copying a portion of this local context, i.e. `./src` to the container.
    2.  Translates to: build the container, tag it with `sq`, use the sqlite-based Dockerfile indicated
    3. Uses entrypoint script inside container just built and runs the same, exposing port 8080.
    4. The entrypoint location is based on contents found inside the docker container. Since the WORKDIR is `opt/src`, the path to the script is simply `scripts/run.sh`

=== "postgres"

    ```sh title="postgres Dockerfile + entrypoint" linenums="1" hl_lines="1 7 8 9"
    docker build --tag pg --file ./deploy/pg/Dockerfile .
    # why ".? (1)
    # exporting to image ...
    # writing image ...
    # naming to docker.io/library/sqlite-django-docker

    docker run --publish 8080:8080 --env-file .env --entrypoint scripts/run.sh \
      --env DATABASE_URL=postgres://db_usr:pw@host.docker.internal:5432/db_pg \
      pg
    # Re: DATABASE_URL: (2)
    # Serve app via gunicorn on 8080 (note connection to postgres://db_usr:pw@host.docker.internal:5432/db_pg)
    # [<time>][INFO] Starting gunicorn 20.1.0
    # [<time>][INFO] Listening at: http://0.0.0.0:8080
    ```

    1. The Dockerfile referenced contains the following instruction `COPY /src to .`. Since I'm at the root directory in running `docker build` the local context is `.` and I'm copying a portion of this local context, i.e. `./src` to the container.
    2. Note that the database credentials employed are those created during [local development](../index.md#use-postgres). This instance of postgres sits in the dev machine and not in a separate docker container. To reach the dev machine from the Docker container, need to use `host.docker.internal` for the host.

## Docker Compose

The above configurations for each pairing of Dockerfile + database to use can become unwieldly.

Note that though I've gotten a container running for the Django web service, I still haven't implemented `redis`, `huey`, and `postgres` as separate containers. Re: `postgres`, I've used the local version of it on my device but I haven't created a separate container for it.

This is where the `compose.yml` becomes handy. I'm able to attach profiles, in this case `pg` and `sq` so that I can simply run:

=== "sqlite"

    ```sh title="compose.debug.yml"

    docker-compose -f compose.debug.yml --profile sq up --build
    # will use sqlite Dockerfile image to build container then run it
    ```

=== "postgres"

    ```sh title="compose.profidebugled.yml"

    docker-compose -f compose.debug.yml  --profile pg up --build
    # will use postgres Dockerfile image to build container then run it
    ```

And this will orchestrate multiple running services: `django`, `redis`, `huey`, and the database, whether `sqlite` or `postgres`, taking into account the "depends_on" field of each service

See the full `compose.debug.yml` which can also be invoked via a just command shortcut: `just debug_up` (assumes 1Password secret reference usage.)

## Command Runner

Requires: `1password`-based secret references

### Container Debug

`just debug_up <target>`

```sh title="Use debugpy on the runserver, must 'Remote Attach' the VS Code debugger separately"
poetry export -f requirements.txt \
  --without-hashes \
  --output src/requirements.txt # (1)

op inject -i ./deploy/env.common.tpl -o ./deploy/.env.debug # (2)

cp ./deploy/compose.debug.yml compose.yml # (3)

docker-compose --file compose.debug.yml \
  --profile {{target}} up \
  --build # (4)
```

1. The Dockerfile referenced in the compose.yml will pip install a `/src/requirements.txt` so `poetry export` ensures that what is installed is always what's declared in `pyproject.toml`

2. Since secrets stored in the .env file are 1Password secret references, I need to inject them into a .env-template; ensure that the `compose.debug.yml` makes use of this same .env-template.

    The .env-file will contain secrets. Hence it's critical it be prefixed `.env` so that this same file will always be included by `.gitignore`.

3. The `compose.yml` file needs to be in the root directory since the build context is `.` and the Dockerfile copies from `/src`.

4. The `<target>` argument refers to a [profile](https://docs.docker.com/compose/profiles/) declared in a `compose.yml` file

### Specific Compose Up

`just up <folder>`

```sh title="Inject secrets in .env file declared in a folder's compose.yml then use it as root compose"
poetry export -f requirements.txt \
  --without-hashes \
  --output src/requirements.txt # (1)

op inject -i ./deploy/{{folder}}/env.tpl -o ./deploy/{{folder}}/.env # (2)

cp ./deploy/{{folder}}/compose.yml compose.yml # (3)

docker-compose up --build
```

1. The Dockerfile referenced in the compose.yml will pip install a `/src/requirements.txt` so `poetry export` ensures that what is installed is always what's declared in `pyproject.toml`

2. Since secrets stored in the .env file are 1Password secret references, I need to inject them into a .env-template; ensure that the `{{folder}}/compose.yml` makes use of this same `{{folder}}/env.tpl`

    The .env-file will contain secrets. Hence it's critical it be named `.env` so that this same file will always be included by `.gitignore`.

3. The `compose.yml` file needs to be in the root directory since the build context is `.` and the Dockerfile copies from `/src`.
