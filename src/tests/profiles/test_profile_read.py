from http import HTTPStatus

from django.template.response import TemplateResponse
from django.urls import reverse


def test_anonymous_profile_view(client, sample_user):
    url = reverse("profiles:detail", kwargs={"username": sample_user.username})
    response = client.get(url)
    assert isinstance(response.template_name, str)
    assert isinstance(response, TemplateResponse)
    assert response.status_code == HTTPStatus.OK
    assert "detail.html" in response.template_name
    assert sample_user.profile.full_name in response.rendered_content
