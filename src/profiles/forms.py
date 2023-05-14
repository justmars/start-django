from allauth.account.forms import SignupForm
from allauth.socialaccount.forms import SignupForm as SocialSignupForm
from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.utils.translation import gettext_lazy as _

from .models import Profile, User


class ConsentBasicForm(SignupForm):
    user_consent = forms.BooleanField(required=True)


class ConsentSocialForm(SocialSignupForm):
    user_consent = forms.BooleanField(required=True)


class EditPersonalData(forms.ModelForm):
    class Meta:
        model = Profile
        fields = (
            "first_name",
            "middle_name",
            "last_name",
            "suffix",
            "gender",
            "date_of_birth",
            "bio",
        )
        exclude = ("user",)
        labels = {"bio": _("About")}
        widgets = {
            "bio": forms.Textarea(attrs={"cols": 80, "rows": 4}),
            "date_of_birth": forms.DateInput(
                attrs={"type": "date", "placeholder": "mm/dd/yyyy (DOB)"}
            ),
        }


class EditProfileImage(forms.ModelForm):
    ALLOWED_TYPES = ["jpg", "jpeg", "png", "gif", "avif", "webp"]

    class Meta:
        model = Profile
        fields = ("image",)
        labels = {"image": _("Profile Image")}

    def clean_image(self):
        im = self.cleaned_data.get("image", None)

        if not im:
            raise forms.ValidationError("Missing image file")

        if not im.name.endswith(("jpg", "jpeg", "png", "avif", "web")):
            raise forms.ValidationError("Invalid file name extension.")

        if im.size > 2 * 1024 * 1024:
            raise forms.ValidationError("File too big, limit 2mb")

        return im


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("email", "username", "first_name", "last_name")


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ("email", "username", "first_name", "last_name")
