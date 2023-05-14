# Facebook Social Authentication

This seems to require a privacy URL and a terms of service URL.

## AllAuth

We need to secure the following values:

Key | Value
:--:|:--:
`FB_ID` | _Client id_
`FB_KEY` | _Client secret_

This is per the configuration we set via django-allauth:

```py title="/config/settings/_auth.py" linenums="1" hl_lines="4 5"
SOCIALACCOUNT_PROVIDERS = {
    "facebook": {
        "APP": {
            "client_id": env("FB_ID", None),
            "secret": env("FB_KEY", None),
            "key": "",
        },
        "METHOD": "js_sdk",
        "SCOPE": ["email", "public_profile"],
        "AUTH_PARAMS": {"auth_type": "reauthenticate"},
        "INIT_PARAMS": {"cookie": True},
        "FIELDS": [
            "id",
            "first_name",
            "last_name",
            "middle_name",
            "name",
            "name_format",
            "picture",
            "short_name",
        ],
        "EXCHANGE_TOKEN": True,
        "VERIFIED_EMAIL": False,
        "VERSION": "v16.0",
        "GRAPH_API_URL": "https://graph.facebook.com/v16.0",
    },
    ...
}
```

(Work in progress.)
