# Design Choices

!!! danger "Functional, local chaos"

    Combining utility classes in html markup results in utter chaos. It makes code look ugly. But...there is a functional appeal to it that's growing on me. Perhaps its strongest suit is what I understand to be [grug](https://grugbrain.dev/)-compatible [locality](https://htmx.org/essays/locality-of-behaviour/). Think "lady in the red dress" in the first Matrix: ostentibly unpleasant yet quite readable.

## `tailwind.config.js`: dawn / dusk

I use `dawn` to signify the light theme and `dusk` to signify the dark theme. The words are uncommon enough that it makes it easy to replace them all in a wholesale _find-all-and-replace_ approach via the IDE, or simply to reuse them by modifying the values found in the Tailwind config file:

```js title="/tailwind.config.js"
module.exports = {
  darkMode: "class", // (1)
  theme: {
    extend: {
      colors: {
        dawn: { // (2)
          darker: "#15803d", // green-700
          DEFAULT: "#16a34a", // green-600
          muted: "#22c55e", // green-500
          lighter: "#86efac", // green-300
        },
        dusk: {
          darker: "#7e22ce", // purple-700
          DEFAULT: "#9333ea", // purple-600
          muted: "#a855f7", // purple-500
          lighter: "#d8b4fe", // purple-300
        },
        grayed: {
          darker: "#334155", // slate-700
          DEFAULT: "#475569", // slate-600
          muted: "#94a3b8", // slate-400
          lighter: "#cbd5e1", // slate-300
        },
      },
    },
  },
}
```

1. Enables theme switching by modifying `<html>` tag
2. The color-number convention, e.g. green-500 refers to the designation found in [TailwindCSS colors](https://tailwindcss.com/docs/customizing-colors).

Note that the named themes can utilize suffixes and prefixes that TailwindCSS is known for, e.g. with `bg-dawn`, `dawn` is a variable I made up, whereas `bg` as a prefix will always mean _apply a background color of CSS variable `dawn`_.

It also becomes easier to implement a custom partial template, particularly with dashed notation that specifies custom accents like `muted`, `lighter`, and `darker`... as well as generic tailwind prefixes like `hover`, `focus-visible`, etc.

## `input.css` definition for buttons, forms

Most of the declarations of utility classes generally happen in common html files.

The definitions of these declarations are automatically made in a single `output.css` file, assuming the [build step](../references/tailwind-setup.md) is running.

However, the `input.css` makes initial adjustments to commonly styled elements:

```css title="Buttons and forms"
@layer base {
  [type="text"],
  [type="email"],
  [type="url"],
  /* etc.; see override source (1) */
  {
    @apply mt-2.5 block w-full rounded-md border-0 px-3.5 py-2 text-sm/6 text-grayed-darker dark:text-grayed-lighter
    /* other tailwind classes */
  }

  button.btn[data-btn="primary"], a.btn[type="button"][data-btn="primary"] {
    @apply text-green-100 dark:text-purple-100 bg-dawn dark:bg-dusk
    /* other tailwind classes */
  }
}
```

1. Overrides selectors foudn in `/node_modules/@tailwindcss/forms/src/index.js`

!!! warning "The controversial `@apply`"

    The [@apply](https://twitter.com/adamwathan/status/1559250403547652097) directive is considered by TailwindCSS maker to be ill-conceived but I find it rather useful to style base elements: specifically buttons and form fields described above. And typing these all out in using the [theme](https://tailwindcss.com/docs/functions-and-directives#theme) directive seems overly verbose. I felt the same about the Tailwind utility classes when they first came out so maybe I'll grow to like the `theme()` convention in time.

## `django-fragments` for skeletal partials

The layout of DOM nodes of html partials is handled by [django-fragments](https://github.com/justmars/django-fragments), especially for icons. The idea is to make this library handle the construction of a building... so that it's ready for a paint job afterwards. See existing partials for:

1. [`{% icon %}`](https://mv3.dev/django-fragments/icon) - idiomatic `<svg>` combiner with neighboring / parent tags

    === "_before_: :simple-django: fragment"

        ```jinja title="Invocation via Django Template Language" linenums="1" hl_lines="2"
        {% load fragments %}{# re: 'x_mark_mini' (1), re: attributes (2) #}
        {% icon name='x_mark_mini' aria_hidden="true" pre_text="Close menu" pre_class="sr-only"  %}

        ```

        1. `name='x_mark_mini'` refers to a heroicon (default) svg copy/pasted into a file named 'heroicon_x.html'
        2. The `aria_hidden` attribute is converted to `aria-hidden`, `pre_text` and `pre_class` means add a `<span class='sr-only'>Close menu<span>` __before__ _(pre_)_ the svg icon.

    === "_after_: html :simple-html5:"

        ```html title="Output HTML after the Template is populated with the Context."
        <span class="sr-only">Close menu</span>
        <svg aria-hidden="true" class="w-6 h-6" fill="none" stroke="currentColor" stroke-width="1.5" viewbox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path d="M6 18L18 6M6 6l12 12" stroke-linecap="round" stroke-linejoin="round">
          </path>
        </svg>
        ```

2. [`{% themer %}`](https://mv3.dev/django-fragments/themer) - `<button onclick=toggleTheme()>` enclosing  two `{% icon %}s`.

    ```js title="/tailwind.config.js"
    module.exports = {
      darkMode: "class", // theme switching via <html> class. // (1)
    }
    ```

    1. `{% themer %}` makes use of js functions `toggleTheme()` from [django-fragments](https://justmars.github.io/django-fragments) to change the class.

    ```jinja title="Overridding defaults"
    {# re: css of sun and moon (1), re: css icon (2) #}
    {% themer icon1_name="sun" icon1_css="dark:hidden icon" icon2_name="moon" icon2_css="hidden dark:block icon" btn_kls="desktop flex justify-center items-center rounded-md transition" %}
    ```

    1. _sun_ has `dark:hidden` + _moon_ has `hidden dark:block`. _TailwindCSS_ translation: if  `<html class='dark'>`: (a) hide _sun_ icon via `:hidden`; (b) make _moon_ icon visible via `:block`.
    2. `icon` as a css class defined in `input.css`

3. [`{% hput %}`](https://mv3.dev/django-fragments/hput) - A limited, simple `<input>`-based `BoundField` + related `<label>`, tags for `help_css`, `label_css` (complements  `django-widget-tweaks`).

    === "_before_: :simple-django: fragment"

        ```jinja title="Invocation via Django Template Language" linenums="1" hl_lines="4"
        {% load fragments %}
        <form method="post" action="{% url 'account_signup' %}">
          {% csrf_token %}
          {% hput form.email kls="fx" %} {# (1) #}
          ...
        </form>
        ```

        1. Must include a classname so that this can be detected by TailwindCSS. Enables future styling to related css targets, e.g. using `.fx`:
            1. `.fx > ul.errorlist`
            2. `.fx > p.help`
            3. `.fx > label`

    === "_after_: html :simple-html5:"

        ```html title="Output HTML after the Template is populated with the Context." linenums="1" hl_lines="3 4 5 6"
        <form method="post" action="/accounts/signup/">
          <input type="hidden" name="csrfmiddlewaretoken" value="xxx">
          <div class="fx">
            <label for="id_email">Email</label>
            <input type="email" name="email" id="id_email">
          </div>
          ...
        </form>
        ```

    !!! info ":simple-django: v5.0"

    The [`BoundField.as_field_group()`](https://docs.djangoproject.com/en/dev/ref/forms/api/#django.forms.BoundField.as_field_group) seems like a viable alternative to use in the future.

    ??? note "TailwindCSS Forms Integration"

        With this setup, I can now use [TailwindCSS forms plugin](https://github.com/tailwindlabs/tailwindcss-forms) and override defaults in `input.css`:

        ```css title="input.css refers to the Tailwind input css file"

        div.fx > ul.errorlist { /* handles errors to be displayed post validation */
          @apply flex flex-col mt-1 ml-1 text-xs sm:text-sm tracking-wide text-pink-500 font-thin
        }

        div.fx > p.help { /* handles the help text */
          @apply flex mt-1 ml-1 text-xs tracking-wide font-thin text-grayed dark:text-grayed-muted
        }

        @layer base {
          /* see forms plugin override */
          [type="text"],
          [type="email"],
          [type="url"],
          [type="password"],
          [type="number"],
          [type="date"],
          [type="datetime-local"],
          [type="month"],
          [type="search"],
          [type="tel"],
          [type="time"],
          [type="week"],
          [multiple],
          textarea,
          select,
          .faux-select /* works in tandem with sel.html */
          {
            @apply mt-2.5 block w-full rounded-md border-0
            px-3.5 py-2 text-sm/6
            text-grayed-darker dark:text-grayed-lighter
            bg-white dark:bg-grayed-darker
            shadow-sm ring-1 ring-inset focus:outline-none focus:ring-1
            ring-gray-300 dark:ring-grayed-darker
            focus:ring-dawn dark:focus:ring-dusk
          }
        }
        ```

        The generate route for forms is to have :simple-django: render the entire form based on model declaration. For more granular controls, i.e. styling the individual components of a field, it's up to the user to reconstruct the form manually. `django-widget-tweaks` help adjust the field itself but the neighboring tags like `<label>`, the wrapping `<div>`, the help text and possible error messages, I think, still need to be managed individually.

        Since the _field template_ from django-fragments is intentionally devoid of style, the only sources that need to be considered in the styling of the `{% hput %}` field are:

        2. any applicable tweaks done by [django-widget-tweaks](https://github.com/jazzband/django-widget-tweaks) when `{% hput ... %}` is first invoked; and
        3. the styled _input.css_, specifically overriding TailwindCSS forms [plugin](https://github.com/tailwindlabs/tailwindcss-forms).

## Sample template tags for inseparable partials

There are some fragments however that cannot be easily separated from the css and javascript involved. They're defined in the `page`'s app and the `base.html` rather than in a third-party library like `django-fragments`. Consider:

1. [`{% sel %}`](./start/select.md) - aria-* and [hyperscript](https://hyperscript.org)ed `<select>`
2. [`{% include '_msg.html' ...  %}`](./start/msg.md) - :simple-django: messages as alerts
