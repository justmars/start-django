# `{% sel %}`

`sel`adopts the model of [django-fragments](https://justmars.github.io/django-fragments) `down-list.html` to create a faked/styled copy of a `<select>` tag.

```jinja title="Invocation" linenums="1" hl_lines="1 6"
{% load start %}{# (1) #}
<form>
  {% hput fld=form.first_name cover="col-span-12 sm:col-span-3" %}
  {% hput fld=form.last_name cover="col-span-12 sm:col-span-3" %}
  {# (2) #}
  {% sel form.suffix idx='sfx-id' cover="col-span-12 sm:col-span-3" %}
  ...
</form>
```

1. Custom template tag from the "pages" app. See `src/pages/templatetags`.
2. It's different from `input` since the template creates a faux select field with a `<div>` rather than using the native `<select>`. Since there can be many select fields in a given parent template, I introduce an identifier `idx` to explicitly segregate fields.
