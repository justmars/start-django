from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from pages.models import Agreement, UserConsent

from .forms import ConsentBasicForm, ConsentSocialForm
from .models import Profile
from .tasks import background_store_img_url


class ConsentBasicAdapter(DefaultAccountAdapter):
    """Override to add user consent."""

    def save_user(self, request, user, form=ConsentBasicForm, commit=True):
        u = super().save_user(request, user, form, commit)
        UserConsent.objects.get_or_create(
            user=u,
            mode=UserConsent.Mode.SIGNUP,
            agreement=Agreement.bind.updated_ver("terms"),
        )
        Profile.objects.get_or_create(user=u)
        return u


class ConsentSocialAdapter(DefaultSocialAccountAdapter):
    """Override to add user consent and social login extracted metadata."""

    def save_user(self, request, sociallogin, form=ConsentSocialForm):
        u = super().save_user(request, sociallogin, form)
        UserConsent.objects.get_or_create(
            user=u,
            mode=UserConsent.Mode.SOCIAL,
            agreement=Agreement.bind.updated_ver("terms"),
        )
        profile, _ = Profile.objects.get_or_create(user=u)
        profile.first_name, profile.last_name = (u.first_name, u.last_name)
        profile.save(update_fields=["first_name", "last_name"])
        if not profile.image:  # profile's image field not yet populated
            if url := u.get_social_url():  # type: ignore
                background_store_img_url(url, profile.image, profile.im_key)
        return u
