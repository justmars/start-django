# Github Social Authentication

!!! tip "Read Context"

    For reusability, ensure to read the discussion on [context](./auth-social.md#context) so that the environment
    variables that are secured can be repurposed for testing in other websites later on.

=== "`local` context :material-thumb-up:"

    Field | Value
    --:|:--
    Homepage url | `http`://127.0.0.1:8000/
    Callback url | `http`://127.0.0.1:8000/accounts/github/login/callback

=== "`container` context :material-thumb-up:"

    Field | Value
    --:|:--
    Homepage url | `http`://0.0.0.0:8080/
    Callback url | `http`://0.0.0.0:8080/accounts/github/login/callback

=== "`site` context :material-thumb-up:"

    Replace `start-django.fly.dev` with the new site.

    Field | Value
    --:|:--
    Homepage url | e.g. `https`://start-django.fly.dev
    Callback url | e.g. `http`://start-django.fly.dev/accounts/github/login/callback/


    !!! warning "An error occurred while attempting to login via your social network account."

        I seem to be receiving redirect mismatch errors. Replacing `https://` with `http://` in the _callback url_ solves the issue. But see [discussion](https://stackoverflow.com/questions/25824598/django-allauth-not-sending-links-with-https); also see AllAuth Advanced Usage in the [docs](https://stackoverflow.com/questions/25824598/django-allauth-not-sending-links-with-https).

## AllAuth

We need to secure the following values:

Key | Value
:--:|:--:
`GITHUB_ID` | _Client id_
`GITHUB_KEY` | _Client secret_

This is per the configuration we set via django-allauth:

```py title="/config/settings/_auth.py" linenums="1" hl_lines="4 5"
SOCIALACCOUNT_PROVIDERS = {
    "github": {
        "APP": {
            "client_id": env("GITHUB_ID", None),
            "secret": env("GITHUB_KEY", None),
            "key": "",
        }
    },
    ...
}
```

We secure these keys via the [Github Console](https://github.com/settings/developers): `OAuth apps`

## Form

![Screenshot of Github oAuth pre-application](/img/github_auth1.png)

Register:

Field  | Value | Description
:--:|:--:|:--:
Application name           | required                                   | Seen in consent screen
Application logo           | optional                                   | Badge of trust in consent screen
Homepage URL               | `site url`                                 | API key / id credential association
Authorization callback URL | `site url`/accounts/github/login/callback/ | Successful login via `allauth`

## Credentials

![Screenshot of Github oAuth post-registration](/img/github_auth2.png)

1. Note _Client id_.
2. Click on generate a _Client secret_.
3. Note warning after secret generated: _Make sure to copy your new client secret now. You won’t be able to see it again._
4. Save id and secret.

## Login Window

![Screenshot of Github oAuth login](/img/github_auth3.png)
