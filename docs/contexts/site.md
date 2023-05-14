# Site

1. Public deployment
    1. Signing up for a cloud service, see Will Vincent's summary of [options](https://learndjango.com/tutorials/django-hosting-deployment-options)
    2. Rolling out your own server.
2. Integrating a remote database
    1. Syncing the remote database with a local version, or a partial segment of it
    2. Ensuring the backup mechanism works
    3. Checking the backup mechanism regularly
3. Reviewing user interactions which ought to be guarded
    1. Cache mechanisms
    2. Rate limiting
    3. User spam
    4. File uploads
4. Being more deliberate with secrets, e.g.
    1. Managing their existence
    2. Limiting hosts
5. Establishing remote logs
6. Focusing more on devops than the actual app created with :simple-django:

## Command Runner

Requires: `fly.toml` pre-configured, `1password`-based secret references

### Deploy app + database with staged decrets

??? tip "`just fly <deployable> <config>`"

    ```sh title="Inject a specific compose.yml with secrets"
    # just set_secrets
    op inject -i ./deploy/env.fly.tpl -o ./deploy/.env.fly
    fly secrets --app {{deployable}} import < ./deploy/.env.fly --stage
    rm ./deploy/.env.fly

    # just deploy
    poetry export -f requirements.txt \
      --without-hashes \
      --output src/requirements.txt

    fly deploy \
      --app {{deployable}} \
      --config ./deploy/{{config}}/fly.toml \
      --dockerfile ./deploy/{{config}}/Dockerfile
    ```

### Stage secrets pre-deploy

??? tip "`just set_secrets <deployable>`"

    ```sh title="Inject a specific compose.yml with secrets"
    op inject -i ./deploy/env.fly.tpl -o ./deploy/.env.fly
    fly secrets --app {{deployable}} import < ./deploy/.env.fly --stage
    rm ./deploy/.env.fly
    ```

### Deploy app with db

`just deploy <deployable> <config>`

    ```sh title="Inject a specific compose.yml with secrets"
    poetry export -f requirements.txt \
      --without-hashes \
      --output src/requirements.txt

    fly deploy \
      --app {{deployable}} \
      --config ./deploy/{{config}}/fly.toml \
      --dockerfile ./deploy/{{config}}/Dockerfile
    ```
