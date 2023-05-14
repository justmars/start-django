from django import forms
from django.db import models
from django.utils.translation import gettext_lazy as _

from .models import Agreement, UserConsent
from .tasks import background_send_contact_form_email


class BasicConsent(forms.ModelForm):
    class Meta:
        model = UserConsent
        fields = ["agreement", "user", "mode"]


class UpdatedPrivacyForm(BasicConsent):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.fields["agreement"] = Agreement.bind.updated_ver("privacy")
        self.fields["mode"] = UserConsent.Mode.PROMPT


class UpdatedTermsForm(BasicConsent):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.fields["agreement"] = Agreement.bind.updated_ver("terms")
        self.fields["mode"] = UserConsent.Mode.PROMPT


class ContactForm(forms.Form):
    class Category(models.TextChoices):
        FEEDBACK = "Code Feedback", _("Code Feedback")
        BUG = "Bug Report", _("Bug Report")
        WORK = "Work Inquiry", _("Work Inquiry")

    email = forms.EmailField(
        label="Email",
        help_text="If you're logged in, this auto-populates.",
    )
    category = forms.TypedChoiceField(
        label="Category",
        choices=Category.choices,
        initial=Category.FEEDBACK,
        help_text="Github issues/discussions also valid place.",
    )
    message = forms.CharField(label="Message", widget=forms.Textarea(attrs={"rows": 3}))

    def send_email(self, form: forms.Form):
        background_send_contact_form_email(
            subject=f"{form.cleaned_data['category']}: {form.cleaned_data['email']}",
            message=f"{form.cleaned_data['message']}",
        )
