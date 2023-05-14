# Setting Up Postgres

!!! note "Optional"

    It's perfectly fine to use `sqlite`. But in the event that you'd like a more robust client-server architecture, the steps below outline how to setup `postgres` in a _local_ [context](../contexts/overview.md).

## Install Postgres Locally

Ensure postgres is [installed](https://www.postgresql.org/download/)

```sh title="Can you run psql?"
psql # enters the postgres shell
# psql (15.2) ...
# postgres=# (1)
```

1. `postgres=#` implies postgres is installed in your machine with 'postgres' as superuser

## Create a Database in Postgres

```psql title="Pre-Django setup inside psql" linenums="1"
postgres=# create user db_usr with password 'pw'; -- (1)
postgres=# create database db_pg; -- (2)
postgres=# grant all privileges on database db_pg to db_usr; -- (3)
postgres=# \c db_pg; -- (4)
You are now connected to database "db_pg" as user "postgres" (superuser)
db_pg=# grant create on schema public to db_usr; -- (4)
db_pg=# alter user db_usr createdb; -- (5)
```

1. `CREATE ROLE` with `user` + `password`
2. `CREATE DATABASE` named `db_pg`
3. `GRANT` link `db_pg` to `user`
4. Need to connect as superuser to grant certain roles to `db_usr`
5. Needed by psycopg3 / django4.2
6. Allow user to create db for running tests

??? post-migration

    After configuration of `DATABASE_URL` in the `.env` file, running either migration command -- `python manage.py makemigrations` or `python manage.py migrate` -- will use the models declared in Django. Running `python manage.py migrate` will produce the necessary tables in postgres.

    ```psql title="\dt shows list of tables post migration"
    postgres=> \c db_pg db_usr;
    You are now connected to database "db_pg" as user "db_usr".
    db_pg=> \dt
                            List of relations
    Schema |              Name              | Type  | Owner
    --------+--------------------------------+-------+--------
    public | account_emailaddress           | table | db_usr
    public | account_emailconfirmation      | table | db_usr
    public | agreements                     | table | db_usr
    public | agreements_authors             | table | db_usr
    public | auth_group                     | table | db_usr
    public | auth_group_permissions         | table | db_usr
    public | auth_permission                | table | db_usr
    public | django_admin_log               | table | db_usr
    public | django_content_type            | table | db_usr
    public | django_migrations              | table | db_usr
    public | django_session                 | table | db_usr
    public | django_site                    | table | db_usr
    public | profiles                       | table | db_usr
    public | profiles_user                  | table | db_usr
    public | profiles_user_groups           | table | db_usr
    public | profiles_user_user_permissions | table | db_usr
    public | socialaccount_socialaccount    | table | db_usr
    public | socialaccount_socialapp        | table | db_usr
    public | socialaccount_socialapp_sites  | table | db_usr
    public | socialaccount_socialtoken      | table | db_usr
    public | user_consents                  | table | db_usr
    ```

??? tip "Delete/reset"

    When necessary, can delete the created database and restart the process:

    ```psql
    db_pg=# \c postgres -- transfer connection
    postgres=# drop database if exists db_pg;
    DROP DATABASE

    -- user can only be deleted after the database it's connected to is deleted
    postgres=# drop user if exists db_usr;
    DROP ROLE
    ```

## Set `DATABASE_URL` in `.env`

One of the initial setup commands is to rename `env.example` from /etc/ to `.env`.

It will contain the sample DATABASE_URL but commented out:

```yaml title="Review env.example" linenums="1" hl_lines="3"
<root>
├── .venv # local virtual environment
├── /etc/env.example # when `just start` runs, a file .env is created in the <root> directory
├── src/ # main project folder
    ├── config/ # project named config
...
```

```sh title=".env"
# locally installed postgres database for start-django
# DATABASE_URL=postgres://db_usr:pw@localhost:5432/db_pg
...
```

Becuse of `DATABASE_URL` being commented out with the initial `#`, the environment variable is not read during runtime. The default `sqlite` :material-database: is then used. To override the behavior, before calling `just start` or a _runserver_ variant, ensure the desired value resides in .`env` during runtime:

```sh title=".env"
DATABASE_URL=postgres://db_usr:pw@localhost:5432/db_pg # note localhost
```

## Django + `DATABASE_URL`

The connection string, `postgres://db_usr:pw@localhost:5432/db_pg`, maps to:

Field | Value | Note
--:|:--|:--
`ENGINE`  | `postgres` | Uses the postgres engine
`NAME` | `db_pg` | `create database db_pg`
`USER` | `db_usr` | `create user db_usr with password 'pw'`
`PASSWORD` | `pw` | `create user db_usr with password 'pw'`
`HOST` | `localhost` | default port in local machine
`PORT` | `5432` | default port in local machine

```py title="Using environs to extract DATABASE_URL"
>>> from environs import Env
>>> env = Env()
>>> env.dj_db_url("DATABASE_URL")
{
  'NAME': 'db_pg',
  'USER': 'db_usr',
  'PASSWORD': 'pw',
  'HOST': 'localhost', # same as "127.0.0.1"
  'PORT': 5432,
  'CONN_MAX_AGE': 0,
  'ENGINE': 'django.db.backends.postgresql_psycopg2'
}
```

According to :simple-django: documentation:

```py title="Sample PostgreSQL settings"
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "mydatabase",
        "USER": "mydatabaseuser",
        "PASSWORD": "mypassword",
        "HOST": "127.0.0.1",
        "PORT": "5432",
    }
}
```

Under `4.2`'s [release notes](https://docs.djangoproject.com/en/4.2/releases/4.2/#psycopg-3-support), `django.db.backends.postgresql_psycopg2` is still valid but the [documentation](https://docs.djangoproject.com/en/4.2/ref/settings/#engine) uses `django.db.backends.postgresql` so I'll change the output of `env.dj_db_url()` via `add_postgres_or_sqlite()` for parity.

```py title="Modified ._settings.py"
...
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
        env.dj_db_url("DATABASE_URL", "sqlite:///db.sqlite")
    )
}
```

The `DATABASE_URL` is consumed in `/src/_settings.py` which modifies the way the original setting
is actually set. The rationale for the modification is that during _deployment_, the `DATABASE_URL` is what is consumed so might as well start with this even during _development_.
