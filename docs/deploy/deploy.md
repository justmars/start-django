# Deployment Proper

## App + database

=== "postgres"

    ```sh title="Attach separate postgres app to fly app"
    fly apps create app_name --machines # ensure app name matches fly.toml (1)
    fly pg create --name pg-xxx-db --region sin  # complete wizard (2)
    fly pg attach pg-xxx-db --app app_name # save DATABASE_URL; how to detach/destroy (3)
    ```

    1. See the fly toml template:

        ```toml title="/pg/fly.toml - same app name" linenums="1" hl_lines="1 5"
        app = "app_name" #
        primary_region = "sin"

        [env]
          DJANGO_ALLOWED_HOSTS = "app_name.fly.dev"  # make sure set here or in fly secrets
        ```

        See [reference](https://fly.io/docs/reference/configuration/#the-app-name)

    2. See the fly toml template:

        ```toml title="/pg/fly.toml - same region" linenums="1" hl_lines="2"
        app = "app_name" #
        primary_region = "sin"
        ...
        ```

    3. When required to delete

        ```sh title="When needed"
        fly pg detach --app start-django pg-xxx-db
        fly apps destroy pg-xxx-db # confirm destruction
        ```

=== "sqlite"

    ```sh title="Create virtual machines in fly with 2 volumes"
    fly apps create xxx --machines # Check fly apps list (1)
    fly vol create <db_vol> --region sin --size 1 -a xxx  # (2)
    fly vol create <db_vol> --region sin --size 1 -a xxx  # (3)
    fly vol list -a xxx # shows 2 items
    ```

    1. See the fly toml template:

        ```toml title="/sq/fly.toml - same app name" linenums="1" hl_lines="1 5"
        app = "app_name" #
        primary_region = "sin"

        [env]
          DJANGO_ALLOWED_HOSTS = "app_name.fly.dev"  # make sure set here or in fly secrets
        ```

        See [reference](https://fly.io/docs/reference/configuration/#the-app-name)

    2. Will receive a prompt prior to creation: _Warning! Individual volumes are pinned to individual hosts. You should create two or more volumes per application. You will have downtime if you only create one. Learn more at https://fly.io/docs/reference/volumes/;_ name only allows alphanumeric characters and underscores. See where to put in the fly.toml template:

        ```toml title="/sq/fly.toml - same app name" linenums="1" hl_lines="5"
        app = "app_name" #
        primary_region = "sin"
        ...
        [mounts]
          source = "<db-vol>"
          destination = "/opt/src/data" # path within container
        ```

        See [reference](https://fly.io/docs/reference/configuration/#the-app-name)

    3. The fly.toml uses 2 processes, if only one volume is created, this will error out: _Error: not enough volumes named start_django_volume (1) to run 2 processes_

    !!! danger "Background workers do not work yet"

        Despite functioning in the [local Docker container context](../contexts/container.md), the same doesn't work in fly. The _worker.sh_ process (which utilizes huey, see fly.toml) can't seem to update an image (e.g. when creating a new account) as a background task. I suspect it's because of the volume. In docker-compose, the volume is shared. In [fly.io](https://fly.io/docs/reference/volumes/):

        > Volumes are independent of one another; Fly.io does not automatically replicate data among the volumes on an app, so if you need the volumes to sync up, your app has to make that happen.

        Looks like I'll have to wait for [LiteFS](https://fly.io/docs/litefs/) or find time to learn an existing early implementation, see example in [usher.dev](https://usher.dev/posts/django-on-flyio-with-litestream-litefs/).

## Secrets + deploy

=== "postgres"

    === ":fontawesome-solid-person-walking-luggage: unpack"

        ```sh title="Be in <root>"
        fly -a app_name secrets import < .env.fly --stage # (1)
        fly -a app_name secrets list # (2)
        fly deploy -a app_name deploy \
        --config ./deploy/pg/fly.toml \
        --dockerfile ./deploy/pg/Dockerfile # (3)
        ```

        1. Add `DJANGO_SECRET_KEY=whatever`, `REDIS_URL=<REDIS_FLY_URL>`, and all third-party service secrets (e.g. `POSTMARK_API_KEY=your-key`, etc.) to `.env.fly` then proceed to deploy. The `--stage` will result in "Secrets have been staged, but not set on VMs. Deploy or update machines in this app for the secrets to take effect."
        2. Review presence of secrets
        3. This should take a few minutes

    === ":material-run-fast: just fly"

        ```sh title="Requires /deploy/.env.fly"
        just fly app_name pg # will use pg config folder to deploy app_name
        ```

=== "sqlite"

    === ":fontawesome-solid-person-walking-luggage: unpack"

        ```sh title="Be in <root>"
        fly -a xxx secrets import < ./deploy/.env.fly --stage # (1)
        fly -a xxx secrets list # (2)
        fly deploy -a xxx deploy \
        --config ./deploy/sq/fly.toml \
        --dockerfile ./deploy/sq/Dockerfile # (3)
        ```

        1. Add `DJANGO_SECRET_KEY=whatever`, `REDIS_URL=<REDIS_FLY_URL>`, and all third-party service secrets (e.g. `POSTMARK_API_KEY=your-key`, etc.) to `.env.fly` then proceed to deploy. The `--stage` will result in "Secrets have been staged, but not set on VMs. Deploy or update machines in this app for the secrets to take effect."
        2. Review presence of secrets
        3. This should take a few minutes

    === ":material-run-fast: just fly"

        ```sh title="Requires /deploy/.env.fly"
        just fly xxx sq # will use sq config folder to deploy xxx
        ```
