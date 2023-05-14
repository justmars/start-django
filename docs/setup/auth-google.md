# Google Social Authentication

!!! tip "Read Context"

    For reusability, ensure to read the discussion on [context](./auth-social.md#context) so that the environment
    variables that are secured can be repurposed for testing in other websites later on.

=== "`local` context :material-thumb-up:"

    Field | Value
    --:|:--
    Homepage url | `http`://127.0.0.1:8000/
    Callback url | `http`://127.0.0.1:8000/accounts/google/login/callback

=== "`container` context :octicons-bug-24:"

    !!! warning "`0.0.0.0:8080` as Google redirect url"

        Cannot register a [container context](./auth-social.md#context) for Google because the redirect uri of `0.0.0.0:8080` does not meet the validation criteria for a valid domain.

=== "`site` context :material-thumb-up:"

    Replace `start-django.fly.dev` with the new site.

    Field | Value
    --:|:--
    Homepage url | e.g. `https`://start-django.fly.dev
    Callback url | e.g. `http`://start-django.fly.dev/accounts/google/login/callback/
    User support email address | Should be part of Google organization
    Developer contact email address | -
    Test user email addresses (< 100) | -

    !!! warning "An error occurred while attempting to login via your social network account."

        I seem to be receiving redirect mismatch errors. Replacing `https://` with `http://` in the _callback url_ solves the issue. But see [discussion](https://stackoverflow.com/questions/25824598/django-allauth-not-sending-links-with-https); also see AllAuth Advanced Usage in the [docs](https://stackoverflow.com/questions/25824598/django-allauth-not-sending-links-with-https).

## AllAuth

We need to secure the following values:

Key | Value
:--:|:--:
`GOOGLE_ID` | _Client id_
`GOOGLE_KEY` | _Client secret_

This is per the configuration we set via django-allauth:

```py title="/config/settings/_auth.py" linenums="1" hl_lines="4 5"
SOCIALACCOUNT_PROVIDERS = {
    "github": {
        "APP": {
            "client_id": env("GOOGLE_ID", None),
            "secret": env("GOOGLE_KEY", None),
            "key": "",
        }
    },
    ...
}
```

Visit [console](https://console.developers.google.com/).

## OAuth consent screen

Create an app:

![Screenshot of Google oAuth consent screen form](/img/google_auth1.png)

According to the `External` User Type for testing:

> Your app will only be available to users you add to the list of test users. Once your app is ready to publish, you may need to verify your app.

Note optional badges of trust

1. App logo
2. Link to privacy policy as a badge of trust
3. Link to terms of service

## Credentials screen

After completing requisites of `OAuth consent screen`, can proceed to securing credentials.

![Screenshot of Google credentials tab](/img/google_auth2.png)

Fields to consider:

Application type | Authorized redirect URI
--:|:--
`Web application` | `https://start-django.fly.dev/accounts/google/login/callback/`

Submit to get _Client id_ and _Client secret_
