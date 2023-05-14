from cloudflare_images.api import CF_DELIVER
from django import template
from django.core.files.storage import storages  # type: ignore
from django.forms import BoundField

register = template.Library()


@register.inclusion_tag("pages/components/sel.html")
def sel(field: BoundField, idx: str, kls: str | None = None) -> dict:
    """Custom `<select>` by populating `pages/component/sel.html`.

    Args:
        field (BoundField): The form field which contains a tuple of choices
        idx (str): Identifier of the field to be created

    Returns:
        dict[str, str]: Values that will populate the inclusion tag partial template `component/sel.html`.
    """  # noqa: E501
    return {"field": field, "idx": idx, "kls": kls}


@register.filter
def variant(url: str, variant: str | None = None):
    """Allow custom filter for Cloudflare Images urls,

    e.g {{ profile.image_url|variant:'avatar' }} becomes `https://url/avatar`

    Assumes that a variant has been set in Cloudflare Images.
    """
    if url and url.startswith(CF_DELIVER) and variant:
        cut = url.removesuffix("/public")
        return "/".join([cut, variant])
    return url


@register.simple_tag
def set_cloudflare_img(id: str, variant: str = "public"):
    """With proper environment variables set, can setup the url from the id"""
    try:
        return storages["cloudflare_images"].url_variant(id, variant)
    except Exception:
        return "/"
