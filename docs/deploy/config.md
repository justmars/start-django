# Post-Deployment Configuration

## Domain Name: `target-app.com`

Since the `fly.toml` field `app` is `deployed-xxx`, the following URL will be usable: `deployed-xxx.fly.dev` and it will have the following IP addresses:

```sh
fly ips list
# VERSION IP                      TYPE            REGION  CREATED AT
# v6      xxxx:xxxx:x::xxx        public          global  1m ago
# v4      yy.yyy.yyy.yyy          public (shared)
# see https://fly.io/docs/flyctl/ips/
```

Assuming I already have a domain that I'd like to attach, how do I make the adjustment?

I connect the `AAAA` value for `deployed-xxx.fly.dev` with the target domain's DNS settings (e.g. namecheap, cloudflare, google domains, etc.)

After this is done, I can add the target like so:

```sh title=""
fly certs add target-app.com
# see https://fly.io/docs/flyctl/certs/
```

Finally, I can add the final url/s to `DJANGO_ALLOWED_HOSTS` to fly secrets:

```sh title="Allow domain as host"
fly secrets set DJANGO_ALLOWED_HOSTS="deployed-xxx.fly.dev,target-app.com"
```

## Add Superuser

Access the admin console at `target-app.com/admin` by creating a superuser

```sh title="Terminal Console"
fly ssh console # (1)
# Connecting to zzz-gibberish-xxx... complete
python opt/src/manage.py createsuperuser # (2)
# Username: xxx
# Email address: yyy@somethingmail.com
# Password: zzz
# Password (again): zzz
# Superuser created successfully.
```

## Revise default `example.com`

### Transactional Email From `example.com`

If we try to signup to test the `POSTMARK_API_KEY`, we'll get a sample email:

!!! success "Sample Email Received"

    Hello from example.com!

    You're receiving this e-mail because user xxx has given your e-mail address to register an account on example.com.

    To confirm this is correct, go to http://deployed-xxx.fly.dev/accounts/confirm-email/MQ:random-text/

    Thank you for using example.com!
    example.com

### Transactional Email from `target-app.com`

We can change the default `example.com` by logging into the admin dashboard with the `superuser` and change `example.com` to `target-app.com`.
