# Repo

The local context gets pushed to a repository online which has its own nuanced set of rules:

1. Setting up github workflow action
2. Determining matrix of tests
3. Adding relevant secrets
4. Ensure local machine tests replicated on repo

## Lint

```yaml title="Lint"
runs-on: ubuntu-latest
steps:
  - uses: actions/checkout@v3
  - name: Setup Python
    uses: actions/setup-python@v4
    with:
      python-version: "3.11"
  - name: Install Dependencies
    run: |
      pip install pre-commit
      pre-commit install-hooks
  - name: Lint with pre-commit
    run: pre-commit run --all-files
```

## Test

```yaml title=".github/workflows/main.yml"
services:
  postgres:
    image: postgres:15
    env:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: postgres
    ports: ['5432:5432']
    options: --health-cmd pg_isready --health-interval 10s --health-timeout 5s --health-retries 5
  ...
name: Testing Python ${{ matrix.python-version }}
  steps:
  - name: Pytest via Sqlite Database Engine
    run: poetry run pytest --ds=config.settings
    working-directory: ./src
  - name: Pytest via Postgres Database Engine
    env:
      DATABASE_URL: 'postgres://postgres:postgres@localhost:${{ job.services.postgres.ports[5432] }}/postgres'
    run: poetry run pytest
    working-directory: ./src
```
