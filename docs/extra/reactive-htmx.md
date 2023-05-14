# Reactive Partials with htmx

!!! tip "Better resources"

    1. [django-htmx](https://github.com/adamchainz/django-htmx)
    2. Django + htmx, [Luke Plant](https://github.com/spookylukey/django-htmx-patterns)
    3. django-htmx-fun, [Thomas Güttler](https://github.com/guettli/django-htmx-fun)
    4. todo, [Jack Linke](https://github.com/jacklinke/django-htmx-todo-list)
    5. pyHAT-stack (https://github.com/PyHAT-stack/awesome-python-htmx)

## _General Rule_: full html page

A typical class-based view (CBV):

```py title="Form constructors"
class ContactForm(forms.Form): # (1)
    ...

class ContactFormView(FormView): # (2)
    template_name = "pages/contact.html"
    form_class = ContactForm
    ...
```

1. May be contained in `forms.py` file but is joined here to illustrate a concept.
2. May be contained in `view.py` file but is joined here to illustrate a concept.

 `ContactFormView` instructs: _on a GET request, render ContactForm in "pages/contact.html"_. Implied in this instruction: __render the full html page__. Django, by design, renders full pages on _every request-response cycle_.

## _Exception_: partial html fragment

 I deviate from the cycle by _no longer_ rendering the full page on submission of the form. See overriden `form_valid()` and `form_invalid()` methods:

```py title="Both methods imply a prior POST request when a form is submitted" linenums="1"
class ContactFormView(FormView):
    ...
    def form_invalid(self, form): # (1)
        return TemplateResponse(self.request, "pages/_contact_form.html", {"form": form})

    def form_valid(self, form): # (2)
        return TemplateResponse(self.request, "pages/_contact_success.html", {})
```

1. The default `form_invalid()` is a `render_to_response()`
2. The default `form_valid()` is a `HttpResponseRedirect()`

What is rendered is a template fragment, emphasized by convention `_<template_name>.html`.

How do we accomplish partial rendering of content? We need to create divisions of the html page so that we can assign parts to render.

Consider an identifiable division of the HTML page represented by `id="contact-form-area"` that can be replaced without touching the other parts of the page.

```jinja title="htmx swapping can target the DOM node" linenums="1" hl_lines="3 10"

<html>
<!-- Other content in the page -->
  <div id="contact-form-area"> {# (1) #}
    <form>
      ...
      <button type="submit"
        hx-post="/contact-form"
        hx-target="#contact-form-area"
      >Let's talk</button>
    </form>  {# (2) #}
  </div>
<!-- Other content in the page -->
</html>

```

1. This allows us to swap the identified element with a replacement fragment.
2. Because of the identified DOM node `id="contact-form-area"`, the _htmx command_ `hx-post` (found in the submit button of the form proper) can render a partial HTML fragment after the form is submitted and the `form_valid()` function is invoked. The fragment will not affect the other parts of the page, only replacing the target `#contact-form-area`.

## Prompt User of Field Error on `form_invalid()`

 On `form_invalid()`, if a _field error_ occurs, the form that is partially rendered will now contain error indicators for the specified field:

```jinja title="Show errors, if existing in the field" linenums="1" hl_lines="5 6 7 8 9"
{% for field in form %} {# (1) #}
  <div class="fieldWrapper">
    {{ field.label_tag }}
    {{ field }}
    {% if field.errors %}  {# (2) #}
      <span class="prominent-tailwind-styling text-pink-500 text-xs">
        {{ field.errors }}
      </span>
    {% endif %}
  </div>
{% endfor %}
```

1. See notes on :simple-django: [making reusable form templates](https://docs.djangoproject.com/en/dev/topics/forms/#reusable-form-templates).
2. Only display when field contains errors.

## Prompt User of Non-Field Error on `form_invalid()`

On `form_invalid()`, if a _non-field error_ occurs, we return the form instance like above but we include htmx-driven alerts itemizing each non-field error.

What is an example of a _non-field_ error? Consider a login form with `email` and `password` fields. The user can supply a random value that is valid, i.e. an email address that is properly formatted, i.e. _john@thisdoesnotexist.com_ However, what if that email address doesn't exist in the database? This would result in a non-field error.

In dealing with such errors, the conventional way of displaying the same is by highlighting the non-field errors above the form. See :simple-django: [Rendering fields manually](https://docs.djangoproject.com/en/dev/topics/forms/#rendering-fields-manually). In contrast, see [Messages as Styled Notifications](https://mv3.dev/django-fragments/architectures/alert)
