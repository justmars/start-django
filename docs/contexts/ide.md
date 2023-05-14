# IDE

## Using / not using type systems

I like typing for the simple reason that it enables me to easily look at the source code from
the IDE :material-microsoft-visual-studio-code:. Consider the following check:

```py title="Import of HttpRequest / TemplateResponse, even if unnecessary." linenums="1" hl_lines="1 2"
from django.http.request import HttpRequest
from django.template.response import TemplateResponse

def public_profile(req: HttpRequest, username: str) -> TemplateResponse:
  return TemplateResponse(
      req,
      "profiles/detail.html",
      {"profile": get_object_or_404(Profile, user__username=username)},
  )
```

I can quickly use the IDE to quickly "go to the definition" of `HttpRequest` or `TemplateResponse`.

!!! note "Perfectionists with deadlines indeed."

    On a non-technical note, red squigglies often evoke the same passion of a bull seeing a red cape so using types alleviates this maddening feeling to a certain extent. And then there's the inane amount of `noqa:` littering that is a pet peeve I need to fix.

## Formatting code on save

=== "`.vscode/settings.json`"

    ```json
    "[python]": {
        "editor.formatOnSave": true,
        "editor.defaultFormatter": "ms-python.black-formatter", // black; see also vscode extension
        "editor.codeActionsOnSave": {
            "source.fixAll": true,
            "source.organizeImports.ruff": true // ruff; see also vscode extension
        },
    },
    ```
=== "`pyproject.toml`"

    ```toml
    [tool.ruff]
    ignore = ["F401", "F403"]
    fixable = ["F", "E", "W", "I001"]
    select = ["F", "E", "W", "I001"]

    [tool.ruff.per-file-ignores]
    "src/config/settings/__init__.py" = ["F405", "E501"]
    "src/config/settings/_auth.py" = ["F405", "E501"]
    "src/config/settings/_settings.py" = ["E501"]
    ```

## Useful extensions

Excluding the non-standard ones:

1. [SQLite](https://marketplace.visualstudio.com/items?itemName=alexcvzz.vscode-sqlite)
2. [Postgres](https://marketplace.visualstudio.com/items?itemName=ckolkman.vscode-postgres)
3. [Python Indent](https://marketplace.visualstudio.com/items?itemName=KevinRose.vsc-python-indent)
4. [python-string-sql](https://marketplace.visualstudio.com/items?itemName=ptweir.python-string-sql)
5. [Tailwind Intellisense](https://marketplace.visualstudio.com/items?itemName=bradlc.vscode-tailwindcss)

## Test Runner

Take advtange of tests already declared in the [local context](./local.md#testing):

!!! tip "`.vscode/settings.json` x pytest"

    ```json
    "python.testing.pytestArgs": [
        "${workspaceFolder}/src", // without this, pytest discovery error
        "--ds=config.settings", // see pytest django
        "--doctest-modules",
        "--exitfirst",
        "--verbose"
      ],
    ```

## Configure Debugger

=== "local"

    No need to setup, just click the _Run and Debug_ button.

    ```json title=".vscode/launch.json"
        {
          "name": "Python: Django Local",
          "type": "python",
          "request": "launch",
          "program": "${workspaceFolder}/src/manage.py",
          "args": [
            "runserver",
            "--noreload",
            "--nothreading",
          ],
          "django": true,
          "cwd": "${workspaceFolder}/src",
        },
    ```

    !!! warning "1Password CLI"

        If using secret references in the `.env` file, i.e. op://, must be based on `auth-local`

=== "container"

    Assuming a `compose.yml` is executed with `debugpy` setup, the `docker-compose` should pause after all services have been started. VS Code's _Run and Debug_ button can be clicked with the following configuration for the debugger to work.

    ```json title=".vscode/launch.json applied to compose.yml"
      {
          "name": "Python: Remote Attach",
          "type": "python",
          "request": "attach",
          "port": 5678,
          "host": "localhost",
          "pathMappings": [
              {
                  "localRoot": "${workspaceFolder}/src",
                  "remoteRoot": "."
              }
          ]
      },
    ```

    !!! warning "1Password CLI"

        If using secret references in the `.env` file, i.e. op://, must be based on `auth-container`

    debuggable | compose | env | shortcut | purpose | note
    :--:|:--:|:--:|:--:|:--:|:--
    yes |compose.debug.yml (copied to root) | Template `env.common.tpl` to populate `.env.debug` for compose.yml | `just debug_up` | attach vscode debugger | uses runserver, lacks ability to debug the background process, might need separate
    no | sq/compose.yml (copied to root) | Template `/deploy/sq/env.tpl` to populate `/deploy/sq/.env` for compose.yml | `just up sq` | check parity on prod | uses gunicorn with an sqlite volume
    no | pg/compose.yml  (copied to root)| Template `/deploy/pg/env.tpl` to populate `/deploy/pg/.env` for compose.yml | `just up pg` | check parity on prod | uses gunicorn, separate postgres container
