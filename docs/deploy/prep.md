# Preflight

!!! warning "Caveat"

    There is a common checklist of things to do with this boilerplate prior to fly.io [deployment](./deploy.md) with either sqlite or postgres.

    More generally, we'll presume all tests are passing, all your secrets are prepared, containerization works as expected, and your local machine has all of fly's necessary tooling.

    Finally, note that while Fly has a generous free tier it requires a credit card to signup.

## Working container

If the `compose.yml.tpl` (in `/pg` and `/sq`) has been tested to work on the different services, e.g. background tasks, image upload, email sending, etc., then it implies that all secrets have been prepared.

### Secrets preparation

Some secrets are sensitive and need to be guarded more securely than others, other secrets are more in the nature of general toggles and can be hard-coded into a config file such as the `compose.yml` or the `fly.toml`.

=== "sensitive .env.fly"

    Key | Note
    --:|:--
    DJANGO_SECRET_KEY | must have one handy; Django-specific; keep safe per project
    REDIS_URL | must have one handy; can be a common url, used in other remote projects
    DATABASE_URL | if using sqlite, need to create a volume and manually set; if postgres, this is generally provided by the service
    POSTMARK_API_KEY | needed for auth / email sending; third-party service
    GOOGLE_ID & GOOGLE_KEY | needed for social auth; third-party service;
    GITHUB_ID & GITHUB_KEY | needed for social auth; third-party service;
    CF_IMG_TOKEN & CF_ACCT_ID & CF_IMG_HASH | needed for ImageField, media (image) storage; third-party service;

    ```yaml title="Project Structure" linenums="1" hl_lines="5 6"
    start-django (root)
    ├── docs/
    ├── src/
    ├── .env # what is used for local setup in machine
    ├── .env.fly # ensure part of .gitignore
    ├── .gitignore # prevent .env / .env.fly.sqlite from being pushed
    ```

    1. Create file, e.g. `.env.fly` at project root
    2. Make sure to add the created file to list of items in `.gitignore`
    3. We'll use `.env.fly` to setup fly secrets later on

=== "toggle fly.toml / compose.yml"

    Key | Note
    --:|:--
    ENV_NAME | dev---test---prod, may be hard-coded in config `fly.toml`, `compose.yml`
    DJANGO_ALLOWED_HOSTS | will only allow connections with fixed values; security measure; may be hard-coded in config `fly.toml`, `compose.yml`
    DJANGO_DEBUG | True---False,  may be hard-coded in config `fly.toml`, `compose.yml`
    EMAIL_RECIPIENT | recipient-email-address-for-contact-form
    EMAIL_SENDER | sender-email-address-for-transactional-emails

    ```toml title="Part of fly.toml"
    ...
    [env]
      ENV_NAME = "test"
      DJANGO_DEBUG = true
      PORT = "8080"
      EMAIL_RECIPIENT = "your-working@email-address-to-receive-emails"
      EMAIL_SENDER = "your-working@email-address-to-send-emails"
      DEFAULT_FROM_EMAIL = "what appears in your email <donotreply@your.domain>"
    ...
    ```

    !!! note "`EMAIL_SENDER`: Transactional Emails"

        This boilerplate uses `python-postmark`, see [github library](https://github.com/themartorana/python-postmark/#django).

        The value of `POSTMARK_SENDER` must first be created in the [postmarkapp](https://https://postmarkapp.com/) website.

        After it's created, can modify both the `POSTMARK_SENDER` and `DEFAULT_FROM_EMAIL` that is declared in `fly.toml`. Note Django's [send_email()](https://docs.djangoproject.com/en/dev/topics/email/#send-mail) which depends on `DEFAULT_FROM_EMAIL`.

### Run Django check

Modify .env by copy/pasting secrets from `.env.fly` to test your future deployment:

```sh
python manage.py check --deploy
```

If satisfied with the results of the check, can proceed to deploy using the variables you've tested with.

## Install fly

[Install flyctl](https://fly.io/docs/hands-on/install-flyctl/) then signup via the commandline.

!!! warning "fly v1 to v2"

    Fly is [presently](https://fly.io/docs/reference/apps/#apps-v2) going through various changes, specifically migrating from _v1_ (called the nomad platform) to _v2_ (running on Fly Machines). The instructions contained here will use _v2_.

    The `fly cli` is frequently being updated. Notes applicable to:

    ```sh title="Terminal Console"
    fly version
    # fly v0.0.538 darwin/arm64 ...
    ```

### Add `REDIS_URL`

If already existing, can simply reuse an existing `REDIS_FLY_URL`. Otherwise, if not yet existing:

```sh title="Note url generated"
fly redis create --name 'reusable-redis-app' # results in REDIS_FLY_URL (1)
```

1. Will receive prompt. "Your Upstash Redis database start-redis-db is ready. Apps in the personal org can connect to at <REDIS_FLY_URL>. If you have redis-cli installed, use fly redis connect to connect to your database." Verify existence via `fly redis list`

### Preconfigured `fly.toml`

Normally for setting up a project, one would run [fly launch](https://fly.io/docs/reference/fly-launch/) - this would generate a `fly.toml` configuration file for use in deploying a project to fly.io.

I've already setup the files for this boilerplate so this step is no longer necessary.

```yaml title="Project Structure" linenums="1" hl_lines="4 7 9"
start-django (root)
├── deploy/
    ├── pg/
        ├── fly.toml
        ├── Dockerfile
    ├── sq/
        ├── fly.toml
        ├── Dockerfile
├── src/
├── .env # what is used for local setup in machine
├── .env.fly # ensure part of .gitignore
├── .gitignore # prevent .env / .env.fly.sqlite from being pushed
```

### Static files in `fly.toml`

```toml title="fly.toml"
...
[[statics]]
guest_path = "/opt/src/static"
url_prefix = "/static"
```

The `whitenoise` library is a dependency declared in `pyproject.toml`. It isn't as useful in
fly.io since I won't be needing Django to serve static files.

The _[statics](https://fly.io/docs/reference/configuration/#the-statics-sections)_ section explains that I can offload this task to fly.io:

> When statics are set, requests under url_prefix that are present as files in guest_path will be delivered directly to clients, bypassing your web server. These assets are _extracted from your Docker image and delivered directly from our proxy on worker hosts_.

In other words, when I set config.settings `STATIC_URL` and then run `python manage.py collectstatic`,
I'm able to place all static files in the Docker image and I can use the location of our Django setting `STATIC_URL` to refer to this content.

### Where to run deploy

!!! note "Where to run `fly deploy`, what context is used"

    Must be in `/root`.

    The `/deploy/pg/Dockerfile` and `/deploy/sq/Dockerfile` will use `COPY /src .` so this implies that the local machine is in the root directory since only a portion of the local machine, `/src` is copied as part of the build context to the container / virtual machine.
