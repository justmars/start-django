# ---
# --- INITIAL SETUP
# ---

# build step tailwindcss
tw :
  npx tailwindcss -i ./src/static/css/input.css -o ./src/static/css/output.css --watch

# update requirements.txt in /src
req:
  poetry export -f requirements.txt \
    --without-hashes \
    --output src/requirements.txt

# prep commit
ante:
  pre-commit run --all-files
  pytest

# quickstart post clone
start:
  if [ -x "$(command -v op)" ]; then just dumpenv; else cp ./etc/env.example.0.dev-op .env; fi
  @echo "\nInitialized .env file"

  @read -p "Setup .venv with poetry?"
  @if ! command -v poetry &> /dev/null; then echo -e "\nPoetry is not installed. You'll need to adjust pyproject.toml to work with your setup."; exit 1; fi
  @poetry install
  @poetry shell

  @read -p "Install tailwind? Enter to continue"
  @if ! command -v npm &> /dev/null; then echo -e "\nnpm is not installed. It's needed to install tailwindcss."; exit 1; fi
  npm install -D tailwindcss \
    @tailwindcss/typography \
    @tailwindcss/forms \
    @tailwindcss/aspect-ratio \
    @tailwindcss/container-queries
  npx tailwindcss -i ./src/static/css/input.css -o ./src/static/css/output.css

  @read -p "Proceed with django setup? Enter to continue"
  just req
  just press
  just db
  pre-commit autoupdate
  pytest
  just run

# undo quickstart post clone
start_undo:
  just ante
  @read -p "Restart entire setup? Enter to continue"
  rm -rf node_modules ./src/staticfiles ./src/mediafiles ./src/static/CACHE ./src/requirements.txt
  rm -fv package-lock.json package.json poetry.lock compose.yml
  rm -rf .venv **/.env

# ---
# --- DJANGO MANAGEMENT
# ---

# collect staticfiles for django-compressor
press:
  rm -rf ./src/static/CACHE
  cd src && python manage.py collectstatic --noinput
  cd src && python manage.py compress --force

# set db
db:
  cd src && python manage.py makemigrations
  cd src && python manage.py migrate

# check common runtime status
status:
  cd src && python manage.py rich

# run_huey: django extensions, may require dumpenv
work:
  cd src && python manage.py run_huey

# shell_plus
sh:
  cd src && python manage.py shell_plus

# runserver_plus: django extensions, may require dumpenv
run:
  open -a "Brave Browser.app" http://127.0.0.1:8000/ && cd src && python manage.py runserver_plus

# ---
# --- DOCKER COMPOSE
# ---

# 1password: inject secrets from to root
dumpenv:
  op inject -i ./etc/env.example.0.dev-op -o .env

# 1password: debug containers with compose.profiled.yml's --profile(sq / pg):
debug_up target:
  just req
  op inject -i ./deploy/env.common.tpl -o ./deploy/.env.debug
  cp ./deploy/compose.debug.yml compose.yml
  docker-compose --profile {{target}} up --build

# 1password: up containers via folder (sq / pg) copied compose.yml:
up folder:
  just req
  op inject -i ./deploy/env.common.tpl -o ./deploy/{{folder}}/.env
  cp ./deploy/{{folder}}/compose.yml compose.yml
  docker-compose up --build

# ---
# --- FLY DEPLOY
# ---

# deploy via config
deploy deployable config:
  just req
  fly deploy \
    --app {{deployable}} \
    --config ./deploy/{{config}}/fly.toml \
    --dockerfile ./deploy/{{config}}/Dockerfile

# 1password: use env.fly.tpl to stage fly app secrets
set_secrets deployable:
  op inject -i ./deploy/env.fly.tpl -o ./deploy/.env.fly
  fly secrets --app {{deployable}} import < ./deploy/.env.fly --stage
  rm ./deploy/.env.fly

# 1password: deploy via config with secrets
fly deployable config:
  just set_secrets {{deployable}}
  just deploy {{deployable}} {{config}}

# serve docs
docs:
  mkdocs serve --config-file ./etc/mkdocs.yml
