# Background Tasks

Run long-running tasks in the background, preventing lag in the request-response cycle. Example tasks included:

1. an upload of user photo
2. sending of contact form details to admin recipient

??? tip "Relationship to async"

    Alternatively (or in tandem), can modify the codebase to make the operation asynchronous. See for instance the implementation of this setup, in relation to long running tasks, in [Running Tasks Concurrently in Django Asynchronous Views](https://fly.io/blog/running-tasks-concurrently-in-django-asynchronous-views/). Might/should explore this setup once I'm able to grasp the async nuances.

## Local Development

!!! note "Connecting the Tooling"

    At this point, I won't delay request-response cycle. I just want to demonstrate the interaction between:

    1. A task defined in :simple-django:
    2. A separate worker process
    3. A message broker

    For this purpose, I need to make some adjustments to the default boilerplate:

    4. `huey` as the running worker process via `run_huey`
    5. another sqlite database, e.g. `huey.db` as the huey message broker

### See task decorator

The function below relates to the storage of an image by a caller function.

Because of the `@task` decorator, if `immediate: False`, the call gets sent to the message broker instead and the function is returned immediately to the caller. This places the task decorated in the job queue to be resolved by `run_huey`.

```py title="profiles/tasks.py" linenums="1" hl_lines="3"
from huey.contrib.djhuey import task

@task()
def background_store_img_form(upload: UploadedFile, name: str, store: Storage) -> str:
    ...
```

This means that the `run_huey` must be operational to handle the queued task.

### Start worker

There are several background task services, the most prominent of which is likely `celery`. Here I'll use `huey` and some [default settings](https://huey.readthedocs.io/en/latest/contrib.html#setting-things-up) with a slight modification:

```py title="config/bases/local.py" linenums="1" hl_lines="3"
...
REDIS_URL = None
HUEY = {"huey_class": "huey.SqliteHuey", "immediate": False} # (1)
```

1. Instead of the default `huey_class`: `huey.RedisHuey` (which the boilerplate changes to `huey.MemoryHuey`), can use `huey.SqliteHuey` as simple message broker to demonstrate the job being consumed:

```sh title="Open New Terminal Console"  linenums="1" hl_lines="7"
python manage.py run_huey
# [2023-03-22 14:20:25,776] INFO:huey.consumer:MainThread:Huey consumer started with 1 thread, PID 71269 at 2023-03-22 06:20:25.776677
# [2023-03-22 14:20:25,776] INFO:huey.consumer:MainThread:Scheduler runs every 1 second(s).
# [2023-03-22 14:20:25,776] INFO:huey.consumer:MainThread:Periodic tasks are enabled.
# [2023-03-22 14:20:25,776] INFO:huey.consumer:MainThread:The following commands are available:
# + profiles.tasks.background_store_img_url
# + profiles.tasks.background_store_img_form # note inclusion of task
...
```

    Without modification, when attempting to `run_huey`, will result in _huey.exceptions.ConfigurationError: Consumer cannot be run with Huey instances where immediate is enabled._

??? info "huey.sqlitehuey vs. redis-server"

    Instead of using sqlite, can opt for `redis-server` running in the background.

    See macOS installation [instructions](https://redis.io/docs/getting-started/installation/install-redis-on-mac-os/). Note this is a global installation on the OS.

    ```sh title="Terminal Console 1"
    python manage.py run_huey
    ```

    ```sh title="Terminal Console 2"
    redis-server # also brew services start redis
    ```

Note `python manage.py run_huey` creates the following files in the `src/` directory:

- `huey.db`
- `huey.db-shm`
- `huey.db-wal`

The `huey.db`, as the message broker, will get populated per task queued.

### Test service

```sh title="Open New Terminal Console"
python manage.py runserver # actual Django app
```

Change a photo from the settings dashboard and this will result in a new task being created in huey.

From the huey console started above, we'll notice 2 new additional lines:

```sh title="Huey Console"  linenums="1" hl_lines="5 6"
...
# [2023-03-22 14:20:25,776] INFO:huey.consumer:MainThread:The following commands are available:
# + profiles.tasks.background_store_img_url
# + profiles.tasks.background_store_img_form # note inclusion of task
# ... INFO:huey:Worker-1:Executing profiles.tasks.background_store_img_form: 45a09254-bd89-4ad5-9bf3-efa7cc964cdf
# ... INFO:huey:Worker-1:profiles.tasks.background_store_img_form: 45a09254-bd89-4ad5-9bf3-efa7cc964cdf executed in 0.005s
```

Inspecting `huey.db`, particularly `kv` table, note new entry added:

```sh title="Using sqlite3 as message broker"
sqlite3 huey.db ".headers on" "select * from kv"
# queue|key|value
# db.sqlite|45a09254-bd89-4ad5-9bf3-efa7cc964cdf|��
```

## Local/Staging Development

Prefatorily, it takes 6-8 seconds before Cloudflare is able to storage a new image associated with a user profile. This means that the user needs to wait for the process to complete before a response can be returned by the view. This makes _Cloudflare Images_ uploads a suitable candidate as a background task.

I'll reproduce the infrastructure described under Local Development to use _Cloudflare Images_ instead of local file storage in saving uploaded image files. This implies using some env variables and getting redis up and running:

```sh title="Add to .env"
ENV_NAME=test # (1)
REDIS_URL=redis://redis:6379/0 # (2)
CF_ACCT_ID=aaa # (3)
CF_IMG_TOKEN=bbb
CF_IMG_HASH=ccc
```

1. Will enable the app use of Cloudflare instead of the local default

    ```py title="See sample implementation in profiles/utils.py used in profiles/models.py" linenums="1" hl_lines="3"
    def select_storage():
      # since ENV_NAME is test, will not use default
      if settings.ENV_NAME == "dev":
          return storages["default"]
      return storages["cloudflare_images"]

    class Profile(models.Model):
      image = models.ImageField(storage=select_storage, blank=True, null=True)
      ...
    ```

2. Implies redis will be running in the background
3. Assumes prior setup of [Cloudflare Images](https://www.mv3.dev/cloudflare-images/)

Run 3 services simultaneously:

=== "Terminal 1"

    ```sh title="Start service 1 in Terminal 1"
    brew services start redis
    # or redis-server if this was installed in a virtual environment
    ```

=== "Terminal 2"

    ```sh title="Start service 2 in Terminal 2, .venv"
    python manage.py run_huey # make sure to be in /src
    ```

=== "Terminal 3"

    ```sh title="Start service 3 in Terminal 3, .venv"
    python manage.py runserver # make sure to be in /src
    ```

Like the scenario above, try changing a photo from the settings dashboard.

This should result in a new task being created in `huey`.

After the request is sent, a response can immediately be returned and the task of uploading an image to _Cloudflare Images_, a long-running task, gets handled by a worker process in the background.

## Docker/Staging Development

### compose

Use `compose.yaml` to build a local _test_ environment that can make use of Cloudflare's API. It puts together the services described above so that it's possible to run the services by interconnected containers:

```yaml title="Partial file /src/compose.yaml defining 4 services: web, db, worker, redis_db" linenums="1"
services:
  db: # may be sqlite or postgres
    ...
  redis_db:
    image: redis:7
    command: redis-server
    ports:
    - "6379:6379"
  web:
    environment:
    - ENV_NAME=test  # app will use Cloudflare API keys declared in .env
    - REDIS_URL=redis://redis_db:6379/0 # declared above
    ...
    command: /opt/src/scripts/run.sh # = gunicorn server
    depends_on:
      - db
      - redis_db
  worker:
    environment:
    - ENV_NAME=test
    - REDIS_URL=redis://redis_db:6379/0
    ...
    command: /opt/src/scripts/worker.sh # = python manage.py run_huey
    depends_on:
      - db
      - redis_db
```

See compose command in [detail](../contexts/container.md)
