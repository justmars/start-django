# Digital Ocean

## Preflight

!!! warning "Stale"

    1. Worked on Digital Ocean's [App Platform](https://www.digitalocean.com/product-tours/app-platform)
    2. Need `runtime.txt`
    3. Push updated project to the github repository
    4. Haven't updated this in awhile

## Create DO App

Create [app](https://cloud.digitalocean.com/apps/new) with **Step 1 / Choose Source**: connect github repository.

## Add Database

Scroll to the bottom of the wizard form of **Step 2 / Configure your app** , start with adding a database named `db`. This is a Django project after all.

Name the database `db`.

## Set WSGI

Append _config.wsgi_ to the default contained in `Run Command` field of **Step 2 / Configure your app**:

## Set Env

In **Step 2 / Configure your app**, the field for environment variables is empty. Set the following:

Key | Value | Description
:--:|:--:|:--:
`DJANGO_ALLOWED_HOSTS` | ${APP_DOMAIN} | This can be configured later hence the brackets
`DATABASE_URL` | ${db.DATABASE_URL} | This assume that the DATABASE is named `db`
`DJANGO_SECRET_KEY`| _Set your own_   | Preconfigure and toggle the "encrypt" checkbox on
`ENV_NAME`  | test  | Preconfigure and toggle the "encrypt" checkbox on

Additionally, can add optional environment variables for social authentication IDs.

## Add Details

On `Next`, **Step 3 / Name your web service**:

1. Select a name
2. Add a data region

## Build App

On `Next`, **Step 4 / Finalize and launch**, select:

1. The pricing plan
2. Number of containers

Then `Launch App` which will proceed to build the component.

Note that as part of auto-detecting python's `requirement.txt` file and determining that it is a python / django application, the build process automatically runs the following command after "Installing requirements with pip":

```zsh
> python manage.py collectstatic --noinput
```

This standard command places all static files - such as images, css, and js - in a single designated output directory previously set by `config.settings.STATIC_ROOT`.

The build process normally takes a few minutes.

## Initialize Database / Admin

Can now run commands in the console such as:

```zsh
> python manage.py migrate # creating the database tables based on Django migration files
```

```zsh
> python manage.py createsuperuser # creating the admin user that can access /admin console
```

## Setup Domain

1. Let's assume previous purchase / control of a `samplesite.com` from NameCheap
2. Visit the `Settings` tab of the console
3. Click on `Edit` in the `Domains` section
4. Click on `Add Domain`
5. Enter the domain in the field
6. Choose `We manage your domain`
7. Secure Digital Ocean `nameservers` e.g.:
   1. ns1.digitalocean.com
   2. ns2.digitalocean.com
   3. ns3.digitalocean.com
8. Visit NameCheap's console related to the purchased `samplesite.com`
9. Add the nameservers
10. DNS name changes can take up to 72 hours.

## Visit Django Admin

1. Use created `superuser` account to login to `samplesite.com/admin`
2. Change the domain name from `example.com` to `samplesite.com`
