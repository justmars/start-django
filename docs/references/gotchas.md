# Gotchas

## Mismatched Keys for Social Auth

Created secret keys for BaseTesting using `127.0.0.1` for the `callback url`. This can be found in 1password `auth-local`

Then setup a new site at `newsite.com`.

Social authentication will no longer work with the newsite. Need a completely new callback url setup for `newsite.com`

## Django Template Tags

Cannot use linebreak in between variables of templatetags, same goes for built-ins like `{% with %}` e.g:

```jinja title="Will prevent template from loading."
{% test
  title='some title'
  caption='some desc'
  cta='some path'
%} {# won't work #}
{% test title='some title' caption='some desc' cta='some path'%} {# works #}
```

See trac issue on [multiline tags](https://code.djangoproject.com/ticket/8652) and [SO question](https://stackoverflow.com/questions/49110044/django-template-tag-on-multiple-line). I hope this issue gets revisited. In an age of inline hyperscript (or even [alpine](https://alpinejs.dev/)), overflowing tailwindcss classes, being able to add multiline custom template tags would definitely be welcome as part of the toolkit. In the same SO thread, a hack was proposed:

```py
>>> import re
>>> from django.template import base
>>> base.tag_re = re.compile(base.tag_re.pattern, re.DOTALL)
# Note the untouched base.tag_re = re.compile(r"({%.*?%}|{{.*?}}|{#.*?#})")
```

But I haven't tried this yet.

## Not in Working Directory (runserver)

```sh title="/root directory"
python manage.py runserver
# python: can't open file '/path/to/start-django/manage.py': [Errno 2] No such file or directory
```

Must be in the proper `WORKDIR`, which is `/src` for local development:

```sh title="/root/src directory" linenums="1" hl_lines="1"
cd src
python manage.py runserver
# System check identified no issues (0 silenced).
# Date time shown
# Django version 4.2, using settings 'config.settings'
# Starting development server at http://127.0.0.1:8000/
# Quit the server with CONTROL-C.
```

## Not in Working Directory (tailwind)

If within the /root/src directory, will not be able to run this properly.

```sh title="root/src directory"
npx tailwindcss -i ./static/css/input.css -o ./static/css/output.css --watch
# Specified input file ./static/css/input.css does not exist.
```

Must be in the root directory since this is where the `tailwind.config.js` file is located:

```sh title="root directory" linenums="1" hl_lines="1"
cd src
npx tailwindcss -i ./src/static/css/input.css -o ./src/static/css/output.css --watch
# Rebuilding...
# Done in 111ms.
```

## Not in Root Directory (mkdocs)

```sh title="/root/src directory"
mkdocs serve
# Error: Config file 'mkdocs.yml' does not exist.
```

Must be in the root directory invoking the config file in the proper path:

```sh title="/root directory" linenums="1" hl_lines="1"
mkdocs serve --config-file ./etc/mkdocs.yml
# INFO     -  Building documentation...
# INFO     -  Cleaning site directory
# INFO     -  Documentation built in 1.05 seconds
# INFO     -  [15:49:54] Watching paths for changes: 'docs', 'mkdocs.yml'
# INFO     -  [15:49:54] Serving on http://127.0.0.1:8001/
```

## Unterminated Processes

When `Access to 127.0.0.1 was denied` shows up as a prompt in the browser:

```sh
mkdocs serve # this should run in port 8001
# When navigation to http://127.0.0.1:8001/, user is shown "Access to 127.0.0.1 was denied."
lsof -i tcp:8001 # (1)
# COMMAND     PID   USER   FD   TYPE             DEVICE SIZE/OFF NODE NAME
# ControlCe 123   xxx    5u  IPv4 0xxxxxx      0t0  TCP *:afs3-fileserver (LISTEN)
# ControlCe 456   xxx    6u  IPv6 0xxxxxx      0t0  TCP *:afs3-fileserver (LISTEN)
kill -9 123 # (2)
kill -9 456
mkdocs serve #
```

1. Look for processes that are still running on a given port
2. Remove all processes on the port

## Accessibility

### Navigation

1. `nav` update of `aria-current`.

### Listbox / Menu

1. Update `aria-activedescendant` of the list node
2. Update `aria-selected` when the role is a `listbox` `option`

## JS gotchas

1. Boolean attributes on comparing boolean values from DOM attributes

## Docker gotchas

1. Sometimes volume data needs to be reset: docker-compose down --rmi all --volumes.

## Wish list

1. Arbitrary list making in django template language
