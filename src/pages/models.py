from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_extensions.db.models import (
    AutoSlugField,
    TimeStampedModel,
    TitleDescriptionModel,
)

from .managers import AgreementRecentManager


class Agreement(TimeStampedModel, TitleDescriptionModel):
    class Category(models.TextChoices):
        """Note all caps used in python, whereas db will save lowercase."""

        TERMS = ("terms", _("Terms of Service"))
        PRIVACY = ("privacy", _("Privacy Policy"))

    slug = AutoSlugField(populate_from=["category", "version"])  # type: ignore
    text = models.TextField()
    version = models.CharField(
        max_length=50,
        help_text="Use dashed notation, e.g. 2-1 to mean version 2.1",
    )
    authors = models.ManyToManyField(get_user_model(), blank=True)
    category = models.CharField(
        max_length=7, choices=Category.choices, default=Category.TERMS
    )

    objects = models.Manager()  # Explicit default
    bind = AgreementRecentManager()  # Most recent agreements

    class Meta:
        db_table = "agreements"
        get_latest_by = ["-version", "-modified"]

    def __str__(self):
        return self.slug


class UserConsent(TimeStampedModel):
    class Mode(models.TextChoices):
        SIGNUP = ("signup", _("Account Signup"))
        SOCIAL = ("social", _("Social Signup"))
        PROMPT = ("prompt", _("Logged-In Prompt"))
        BANNER = ("banner", _("Banner Pop-Up"))

    agreement = models.ForeignKey(Agreement, on_delete=models.CASCADE)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    mode = models.CharField(max_length=7, choices=Mode.choices, default=Mode.SIGNUP)

    class Meta:
        db_table = "user_consents"
