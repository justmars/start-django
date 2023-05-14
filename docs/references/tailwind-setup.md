# Tailwinding Django

## `output.css`

### The File

The goal is to finalize an `output.css` definition file covering utility classes declared in templates.

```jinja title="/src/templates/base.html" linenums="1" hl_lines="5"
<html>
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="{% static 'css/output.css' %}">
  </head>
  ...
</html>
```

Tailwind's build step is intended to be running the entire time during development.

So while I'm modifying applicable templates, the build step will _constantly change_ the `output.css` file.

As an example, when I add a never-before used utility class, e.g. `bg-orange-400` to a Tailwind-discoverable template fragment, the build process will modify the `output.css` so that the definition of `bg-orange-500` is created in the `output.css` file (which is then cascaded by `base.html` to the entire website.)

### The Templates

The question then arises, _how do I make the files discoverable_ so that definitions are automatically added?

This is a partial fragment of the present settings:

```py title="/src/config/settings/_settings.py" linenums="1" hl_lines="2 6"
...
STATICFILES_DIRS = [str(BASE_DIR / "static")] # (1)
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],  # (2)
        "OPTIONS": {"context_processors": [...]},
    },
]
```

1. In the event that I use Tailwind classes in js files, which are found in `/src/static/js`, I'll want Tailwind to automatically create the definitions.
2. I'll definitely be using Tailwind classes in html files and these are found in `/src/templates`.

By simple declarations in the config file, Tailwind is instructed to discover utility classes in these filetypes found in specified locations:

```js title="/tailwind.config.js" linenums="1" hl_lines="4"
/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: "class",
  content: [ // (1)
    "src/templates/**/*.{html,js}", // (2)
    "src/static/js/**/*.js", // (3)
  ],
  plugins:  [...] // already populated,
}
```

1. Add the locations here or follow the more [dynamic approach described by Carlton Gibson](https://noumenal.es/notes/tailwind/django-integration/)
2. See `STATICFILES_DIRS` (`/src/static`)
3. See `TEMPLATES[0][DIRS]` (`/src/templates`)

### The Build Step

Now that we know what to look for, where to look for them, and the eventual destination of the definitions... _how do we start the process?_ Tailwind's build process command, touched on earlier, needs to _run separately_ from Django's `runserver` command.

```sh title="In a separate terminal console"
npx tailwindcss \ # build process
-i ./static/css/input.css \ # (1)
-o ./static/css/output.css \ # (2)
--watch # will run in the background
```

1. `-i` is shorthand for `--input`
2. `-o` is shorthand for `--output`

It will simply watch for changes made in Tailwind's required `input.css` and the `content` location values found in `tailwind.config.js`. Every time a change is made, the `output.css` file is either created or updated.

Since the command is a bit verbose, I've created a shortcut with `just tw`.

## Installation

!!! info "TailwindCSS Native"

    [django-tailwind](https://pypi.org/project/django-tailwind/) integrates better but I prefer the manual process in case I need to make adjustments later on.

!!! warning "Reminders Only"

    The steps here are outlined so that I'm reminded on how I prepared the present `tailwind.config.js`

### Install `/node_modules`

The `node_modules` folder is hosted in the root project folder. These our necessary to continuously generate the `output.css`:

```sh title="/node_modules"
npm install -D tailwindcss \
  @tailwindcss/typography \
  @tailwindcss/forms \
  @tailwindcss/aspect-ratio \
  @tailwindcss/container-queries # (1)
```

1. Check that the `/node_modules` contains the plugin folders.

To prevent git inclusion of the `/node_modules` folder, add to the root folder's `.gitignore` file:

```txt title=".gitignore" linenums="1" hl_lines="3"
.DS_Store
.ruff_cache
node_modules
...
```

### Create config file

Initialize the configuration file.

```sh title="Create tailwind.config.js"
npx tailwindcss init # generates near empty config
```

### Add installed `node_modules`

Add plugins installed above to the config file.

```js title="/tailwind.config.js" linenums="1" hl_lines="5"
/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: "class",
  content: [],
  plugins:  [ // (1)
    require("@tailwindcss/typography"),
    require("@tailwindcss/forms"),
    require("@tailwindcss/aspect-ratio"),
    require("@tailwindcss/container-queries"),
  ],
}
```

### Entrypoint `input.css`

For the `output.css` to be built, I need to ensure an `input.css`, conventional name recommended in Tailwind's installation [docs](https://tailwindcss.com/docs/installation).

I create this under `./static/` with basic directives (but modify it later on):

```css title="/src/static/input.css"
@tailwind base;
@tailwind components;
@tailwind utilities;
```

## Compression

Generating `output.css` covering Django html templates and other static files will likely result in multiple, large files. This can be optimized. `django-compressor` is an optimization tool to make multiple files into a single cacheable unit. Though this also applies to javascript files, the following documentation relates to the `output.css` produced by TailwindCSS.

### Install compressor

```sh title="Can also use pip, etc."
poetry add django-compressor
```

```py title="config.settings.base.py" linenums="1" hl_lines="3 7 8 9 10 13"
INSTALLED_APPS = [
    "django.contrib.staticfiles",
    "compressor",
    ...
]
# see https://django-compressor.readthedocs.io/en/stable/
STATIC_ROOT = BASE_DIR / "staticfiles"  # (1)
COMPRESS_ROOT = BASE_DIR / "static" # (2)
COMPRESS_ENABLED = True # (3)
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",  # default
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",  # default
    "compressor.finders.CompressorFinder", # (4)
]
```

1. Where all the staticfiles are gathered after running `python manage.py collectstatic --noinput`
2. This is where the `/CACHE` folder will be created, i.e. `src/static/CACHE`. So after running `python manage.py compress`, we can expect `/css` and `/js` subfolders under `/CACHE`
3. Allow compression even when `DEBUG` is True. See `COMPRESS_ENABLED` setting in `django-compressor` docs.
4. _"In case you use Django's staticfiles contrib app you have to add Django Compressor's file finder to the `STATICFILES_FINDERS` setting"_ - `django-compressor` quickstart.

### Use compress tag

The tailwind-generated `output.css` file in the `base.html` will now be constantly compressed into a cached, optimized file. See [example result](https://django-compressor.readthedocs.io/en/stable/usage.html#examples).

```jinja title="base.html x output.css" linenums="2" hl_lines="2 9 10 11"
{% load static %}
{% load compress %} {# (1) #}
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1">
    ...
    {% compress css %}
      <link rel="stylesheet" href="{% static 'css/output.css' %}"> {# (2) #}
    {% endcompress %}
    ...
  </head>
</html>
```

1. Allows use of `{% compress css %}` and `{% compress js %}` tags.
2. All stylesheets included between the `{% compress css %}` and `{% endcompress %}` tags will be compressed into a single `/static/CACHE/css` file.

### Collection before compression

```sh title="Produce cached files from output.css"
# while in /src; note usage in scripts/web.sh and scripts/run.sh
python manage.py collectstatic --noinput  # (1)
python manage.py compress --force # (2)
```

1. Place files in the `STATIC_ROOT` folder, `--noinput` flag implies the user is not prompted for any kind of input.
2. If `COMPRESS_OFFLINE` is `False` (default), can use `python manage.py compress --force` to override. The `compress` management command produces the `manifest.json`

Based on the above flow, static files from many sources (including the admin) are collected and then subsequently compressed into a single css / js file found in the `static/CACHE`, mapped out via a generated `manifest.json` file.
