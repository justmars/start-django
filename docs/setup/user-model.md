# Custom User Model

## Authentication

_How do I manage signup and login in Django?_

Authentication is pretty complex. Thankfully, third-party packages are available to make this more manageable:

1. [django-allauth](https://www.intenct.nl/projects/django-allauth/)
2. [Authlib](https://github.com/lepture/authlib)

I use _allauth_ in this boilerplate so users are able to sign up via:

Authentication Mode | Description
--:|:--
[Email](./auth-email.md) | Email signup via email address and password
[Social](./auth-social.md) | Signup via Google and Github

Maybe in the future, I can explore:

1. login via mobile number
2. magic email links (e.g. Slack)

## Profiled User Consent

### User

Once a user is authenticated, a table in the database gets populated. What table? If I didn't modify the Django project, it would be the table represented by `auth.User`. The following setting however overrides the default:

```py title="Override default 'auth.User'"
AUTH_USER_MODEL = "profiles.User" # (1)
```

1. This overrides the default 'auth.User'. See :simple-django: [reference](https://docs.djangoproject.com/en/dev/ref/settings/#auth-user-model)

    From the :simple-django: [docs](https://docs.djangoproject.com/en/dev/topics/auth/customizing/#substituting-a-custom-user-model):

    > Some kinds of projects may have authentication requirements for which Django’s built-in User model is not always appropriate. For instance, on some sites it makes more sense to use an email address as your identification token instead of a username.

    The rationale for overriding the default can be found in a :simple-django: [warning](https://docs.djangoproject.com/en/dev/ref/settings/#auth-user-model):

    > You cannot change the `AUTH_USER_MODEL` setting during the lifetime of a project (i.e. once you have made and migrated models that depend on it) without serious effort. It is intended to be set at the project start, and the model it refers to must be available in the first migration of the app that it lives in...

    Elaborating [further](https://docs.djangoproject.com/en/dev/topics/auth/customizing/#changing-to-a-custom-user-model-mid-project):

    > Changing `AUTH_USER_MODEL` after you’ve created database tables is significantly more difficult since it affects foreign keys and many-to-many relationships, for example.
    >
    > This change can’t be done automatically and requires manually fixing your schema, moving your data from the old user table, and possibly manually reapplying some migrations...

### Profile

I don't modify the new overriden `User` at all, preferring to create a dedicated `Profile` model / table that details the authenticated `User`.

```py title="profiles/models.py: the Profile Model" linenums="1" hl_lines="3 8"
from django.contrib.auth.models import AbstractUser

class User(AbstractUser): # AbstractUser: username, email, first_name, last_name
    ... # deliberately empty, just an override (just in case)

class Profile(TimeStampedModel):
    ...
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True)
    image = models.ImageField(storage=select_storage, blank=True, null=True)
    ...
```

### Consent

The user, more often than not, is asked on signup to agree to the site's terms and conditions prior to proceeding.

For purposes of compliance (I'm a lawyer), I'd like to be able to monitor consent and later on be able to make changes to the terms and conditions (and secure later consent for those changes as well). How do I go about this? I create another set of models in the `pages` app that map agreements to consenting users:

```py title="/src/pages/models.py: Consent"
class Agreement(TimeStampedModel, TitleDescriptionModel):
    class Category(models.TextChoices):
        TERMS = ("terms", _("Terms of Service"))
        PRIVACY = ("privacy", _("Privacy Policy"))
    ... # fields related to the agreement

class UserConsent(TimeStampedModel):
    class Mode(models.TextChoices):
        SIGNUP = ("signup", _("Account Signup"))
        SOCIAL = ("social", _("Social Signup"))
        PROMPT = ("prompt", _("Logged-In Prompt"))
        BANNER = ("banner", _("Banner Pop-Up"))

    agreement = models.ForeignKey(Agreement, on_delete=models.CASCADE)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    mode = models.CharField(
        max_length=7, choices=Mode.choices, default=Mode.SIGNUP
    )
```

### Consent + Profile on User Signup

Putting the _User_, _Profile_, and _UserConsent_ together, I override [django-allauth adapters](https://django-allauth.readthedocs.io/en/latest/advanced.html#creating-and-populating-user-instances) for both email and social signup processes.  This is what the overriden social adapter looks like:

```py title="/src/profiles/adapters.py"
class ConsentSocialAdapter(DefaultSocialAccountAdapter):
    def save_user(self, request, sociallogin, form=ConsentSocialForm):
        u = super().save_user(request, sociallogin, form)
        consent = UserConsent.objects.create(
            user=u,
            mode=UserConsent.Mode.SOCIAL,
            agreement=Agreement.bind.updated_ver("terms"),
        )
        profile, _ = Profile.objects.get_or_create(user=u)
        profile = consent.user.profile  # type: ignore
        profile.first_name, profile.last_name = (u.first_name, u.last_name)
        profile.save(update_fields=["first_name", "last_name"])
        if not profile.image:  # profile's image field not yet populated
            if url := u.get_social_url():  # type: ignore
                background_store_img_url(url, profile.image, profile.im_key)
        return u
```

In sum, if you want to sign up, regardless of the mode, consent to the terms before registration.

## User-Adjustable Profile Settings

<figure markdown>
  ![Screenshot of the user settings page with various tabs](https://imagedelivery.net/LLeh8mnCUoU0BaD7C8j7eQ/d0d4b047-9210-4d76-eb4b-306430b8a000/public)
  <figcaption>Screenshot of the user settings page with various tabs</figcaption>
</figure>

The boilerplate saves time by pre-styling the otherwise vanilla UI templates of _django-allauth_. The user dashboard can be accessed by creating an account and logging in. In this dashboard, the following areas can be set:

Area | Description
--:|:--
_Personal Data_ | name / bio fields
_Email_ | `django-allauth`-driven; enables addition and removal of email adds associated with the account
_Password_ | `django-allauth`-driven; sets password, for social login accounts, and enables changing it if the password already set
_Social Login_ |  `django-allauth`-driven; connect, disconnect social accounts
_Account Settings_ | deletion, user avatar

## :simple-django: Settings on the User Model

!!! warning "Separate settings for auth, email, social"

    ```yaml title="Authentication" linenums="1" hl_lines="6"
    <root>
    ├── src/
        ├── config/ # project named config
            ├── settings/
                ├── __init__.py # switch env: dev | test | prod
                ├── _auth.py # auth, email, social
                ├── _settings.py # base settings
        ├── static/
    ...
    ```

    There are a lot of settings related to authentication. So much so that I think it deserves its own settings file rather than being lumped together with everything else.

    So for this boilerplate, I separate `settings/_auth.py` from the base `settings/_settings.py`. This makes it easier for me to make changes to a file devoted specifically to the user.
