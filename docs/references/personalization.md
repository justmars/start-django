# Customization

## Post-installation

1. Add to `.gitignore`: `.vscode`
2. Revise `README.md`.
3. Delete `/docs`
4. Reset source git: `rm -rf .git`

## Revise pyproject.toml

```toml title="Insert your own values"
[tool.poetry]
name = "your app"
version = "0.0.1"
description = "your description"
authors = ["your name <your@email>"]
```

## Adjust initial content

```yaml title="/src/static/img"
<root>
├── docs/ # can delete/modify this
├── src/ # main project folder
    ├── pages/
        ├── fixtures/
            ├── home.yml # list of features in Home, maps pages/views.py
            ├── legal.yml # where to place contracts / agreements
            ├── x.yml # list of repos in Popular, maps to pages/views.py
    ├── templates/
        ├── svg/ # where all the icons used by the boilerplate are stored
```

## Enable Search

```html title="base.html" linenums="1" hl_lines="5"
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="robots" content="noindex"> # delete this line
    ...
  </head>
  ...
</html>
```

## Change Favicons

```yaml title="/src/static/img" linenums="1" hl_lines="5 8"
<root>
├── src/ # main project folder
    ├── static/
        ├── css/
        ├── img/ # find / replace here
        ├── js/
    ├── templates/
        ├── base.html
```

```html title="Ensure replaced files match in base.html" linenums="1" hl_lines="4 5 6 7 8"
<html lang="en">
  <head>
    ...
    <link rel="shortcut icon" type="image/png" href="{% static 'img/favicons/favicon.ico' %}"/>
    <link rel="apple-touch-icon" sizes="180x180" href="{% static 'img/favicons/apple-touch-icon.png' %}">
    <link rel="icon" type="image/png" sizes="32x32" href="{% static 'img/favicons/favicon-32x32.png' %}">
    <link rel="icon" type="image/png" sizes="16x16" href="{% static 'img/favicons/favicon-16x16.png' %}">
    <link rel="manifest" href="{% static 'img/favicons/site.webmanifest' %}">{# List of icons #}
    ...
  </head>
  ...
</html>
```

## Finalize Social Auth Secrets

If social auth does not work, look at the error, e.g. `redirect-uri-mismatch`. It may mean that the _homepage_ url and the _callback_ url must be first set to _http_ since the site is not yet configured for _https_. Reset social auth secrets specific to the url, taking into account the host for the callback url, so that the proper callback url matches the production url.
