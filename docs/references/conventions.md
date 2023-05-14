# Conventions Adopted

## Notable elements

Element | Description
--|:--
`alert-hq` | Identifies the global notification area DOM node for showing Django-based messages. See [messages](/features/3-message-notifications/).
`background_<verb_noun>` | Function name convention using a prefix `background_` denotes a process, described by `<verb_noun>`, to be undertaken in the background to avoid delaying the request-response cycle. See [background tasks](/features/6-background-tasks/).
`_<template-name>.html` | Filename convention using an prefix `_` denotes partial template fragment

## htmx-based Views

Aspect | Convention | Signifies What | Example
--:|:--:|:--:|:--
_prefix_ | `view_` |  `view_` generic `HttpResponse` | `view_whatever` retrieves full page `TemplateResponse`
_prefix_ | `hx_` |  htmx-styled request/response |  `hx_personal_data_get` retrieves partial HTML fragment containing `EditPersonalData` form
_suffix_ | `_get` | implies `hx_` prefixed `<form method=GET>` views | `hx_personal_data_get` (see above) shows unbound form
_suffix_ | `_post` | implies `hx_` prefixed `<form method=POST>` views | `hx_personal_data_post` accepts bound `hx_personal_data_get` form

## Functional View Code Style

```py title="app/views.py"
from django.http.request import HttpRequest # applied typing
from django.template.response import TemplateResponse # applied typing
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET

@never_cache # sample use of cache decorator
@require_GET # explicit vs. implicit
def view_whatever(request: HttpRequest, whatever: str) -> TemplateResponse:
    ctx = {"key": "some_value"} # include context variables in template.html
    res = TemplateResponse(request, "templates/template.html", ctx) # one-liner
    res['HX-Trigger'] = "SOMETHING" # enables modifying response before rendering
    return res # compare delayed res vs. `return render(request, template, ctx)`
```

## URL Patterns

```py title="app/urls.py"
from django.urls import path
from django.urls.resolvers import URLPattern # applied typing

from .views import view_whatever, hx_personal_data_post

app_name = "profiles" # namespaced urls
urlpatterns: list[URLPattern] = [
    # explicit use of path function arguments; trailing comma
    path(
        route="detail/<slug:whatever>",
        view=view_whatever,
        name="detail",
    ),
    path(
        route="name_bio/post", # ends in form method
        view=hx_personal_data_post, # same as name, if possible
        name="hx_personal_data_post",
    ),
    ...]
```
