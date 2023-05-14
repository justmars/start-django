# Setup Overview

## Files

```yaml title="Project structure"
<root>
├── src/ # main project folder
    ├── data/ # where sqlite database should be stored
    ├── config/ # project named config
        ├── settings/
            ├── __init__.py # switch env: dev | test | prod
            ├── _auth.py # django_allauth, postmark email
            ├── _settings.py # base settings
    ├── static/
    ├── profiles/ # custom user + profile model app, manages user settings
    ├── pages/ # legalase + userconsent, basic pages, UI components
    ├── scripts/ # entrypoint for compose.yml, fly.toml
    ├── templates/ # contains base.html
        ├── account/ # overrides django-allauth html templates
        ├── socialaccount/ # overrides django-allauth html templates
        ├── svg/ # used by django-fragments
    ├── tests/ # with pytest-django
    ├── manage.py # management command
```

## Default

Aspect | Scenario | Configuration | Expected Result
:--:|:--|:--|:--
:material-database: | Defaults to `sqlite`. | If `postgres` desired, ensure `DATABASE_URL` setup in [.env](./use-postgres.md) before running `just start` | Local postgres instance used
:material-email: | Emails default to `stdout` | Setup [Postmark](./email-postmark.md) (note, only 100/free per month) | Transactional emails (and the contact form) will use Postmark to deliver emails
:material-image: | Images use local file storage system |Setup [Cloudflare Images](./cloudflare-images.md) (note, $5 per month) | Images uploaded/changed will be stored in Cloudflare Images
:material-github: | Social auth errors out, e.g. _"Cannot encode None for key 'client_id' in a query string. Did you mean to pass an empty string or omit the value?"_ | Setup [Google env vars](./auth-google.md),  [Github env vars](./auth-github.md) | User can use Google and Github to signup without creating a password
:material-wrench-check: | Background processes default to `{"immediate": True}`, i.e. no worker queue | Use either `ENV_NAME` 'test' or 'prod'

## Prelims

Transactional emails :material-email-off:, remote storage :material-cloud-off:, social auth :simple-github: will not yet be cloud-ready until configured. If setting up these services for the first time, can expect this to take 15min to an hour. When addressed, `.env` can be populated with relevant key-value pairs:

```sh title="Expected .env file values"
# postmarkapp.com for transactional emails
POSTMARK_API_KEY=op://dev/postmark/credential

# recipient email address for contact form
EMAIL_RECIPIENT=op://dev/start-django/email/recipient

# sender email address for transactional emails, configured with postmark
EMAIL_SENDER=op://dev/start-django/email/sender

# django-allauth social auth with google as provider
GOOGLE_ID=op://dev/auth-local/google/id
GOOGLE_KEY=op://dev/auth-local/google/secret

# django-allauth social auth with github as provider
GITHUB_ID=op://dev/auth-local/github/id
GITHUB_KEY=op://dev/auth-local/github/secret

# cloudflare images as storage class
CF_ACCT_ID=op://dev/cf-img/acct_id
CF_IMG_TOKEN=op://dev/cf-img/token
CF_IMG_HASH=op://dev/cf-img/hash
```

`op://` is a :simple-1password: convention for [secret references in .env](https://developer.1password.com/docs/cli/secret-references). Unnecessary if you don't use 1Password; can be replaced directly by explicit values, e.g. `DJANGO_SECRET_KEY=i-am-a-value`.
