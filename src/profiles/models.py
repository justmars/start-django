from django.contrib.auth.models import AbstractUser
from django.core.exceptions import PermissionDenied
from django.db import models
from django.shortcuts import get_object_or_404
from django.templatetags.static import static
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django_extensions.db.models import TimeStampedModel

from .utils import select_storage, set_base_img_url


class User(AbstractUser):
    def get_absolute_url(self):
        return reverse("profiles:detail", kwargs={"username": self.username})

    def get_social_url(self) -> str | None:
        socials = self.socialaccount_set  # type: ignore ; see django-allauth
        if socials.count():  # type: ignore ; see django-allauth
            return set_base_img_url(socials.first().get_avatar_url())
        return None


class Profile(TimeStampedModel):
    """Creates some common properties:

    @property | description
    --:|:--
    `image_url` | The saved image related to the profile; if a `social_url` exists on signup, this is automatically used to create the `image_url`.
    `im_key` | Prevent duplicate names saved on file storage by establishing a convention for storing image files on each Profile

    """  # noqa: E501

    SuffixChoices = [
        ("Jr.", "Jr."),
        ("Sr.", "Sr."),
        ("III", "III"),
        ("IV", "IV"),
        ("V", "V"),
        ("VI", "VI"),
    ]
    GenderChoices = [("Male", "Male"), ("Female", "Female")]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True)
    image = models.ImageField(storage=select_storage, blank=True, null=True)
    first_name = models.CharField(max_length=250, blank=True, null=True)
    middle_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=250, blank=True, null=True)
    suffix = models.CharField(
        max_length=3, choices=SuffixChoices, blank=True, null=True
    )
    gender = models.CharField(
        max_length=7, choices=GenderChoices, blank=True, null=True
    )
    date_of_birth = models.DateField(_("Date of Birth"), blank=True, null=True)
    full_name = models.CharField(max_length=250)

    class Meta:
        db_table = "profiles"
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"

    def __str__(self):
        if self.user.first_name != "" and self.user.last_name != "":
            fields = (self.first_name, self.last_name, self.suffix)
            return " ".join(f for f in fields if f)
        return str(self.user.username)

    def save(self, *args, **kwargs):
        self.full_name = str(self)
        super().save()  # Call the real save() method

    @classmethod
    def get_for_user(cls, profile_id: int, user: User):
        """Simple permission checking"""
        profile = get_object_or_404(cls, id=profile_id)
        if profile.user != user:
            raise PermissionDenied()
        return profile

    @cached_property
    def im_key(self):
        """Identifying key for image to store."""
        return f"profiles/{self.user.username}"

    @property
    def image_url(self) -> str:
        """URL to stored image object of user profile (or default)."""
        if self.image:
            if self.image.name.startswith("https://"):
                return self.image.name
            elif self.image.storage.exists(self.image.name):
                return self.image.storage.url(self.image.name)
        return static("img/smiler.png")
