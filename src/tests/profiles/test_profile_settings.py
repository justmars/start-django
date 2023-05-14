from http import HTTPStatus

import pytest
from django.contrib.auth import get_user_model
from django.http.response import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse
from profiles.views import tab_personal_data


@pytest.mark.parametrize(
    "urlpattern",
    [
        "profiles:settings",
        "account_email",
        "account_set_password",
        "account_change_password",
        "socialaccount_connections",
    ],
)
def test_anonymous_user_viewing_settings(client, urlpattern):
    login_first = reverse("account_login")
    attempt_url = reverse(urlpattern)
    response = client.get(attempt_url)
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == f"{login_first}?next={attempt_url}"


def test_hx_personal_data_get(rf, sample_user):
    request = rf.get(reverse("profiles:settings"))
    request.user = sample_user
    response = tab_personal_data(request)
    assert isinstance(response, TemplateResponse)
    assert response.status_code == HTTPStatus.OK
    assert response.template_name == "profiles/tab_personal.html"


def test_hx_personal_data_post(client, sample_user):
    test_this = "XXX___XXX___XXX"
    test_user = get_user_model().objects.get(email=sample_user.email)
    path = reverse("profiles:hx_personal_data_post")
    client.force_login(test_user)
    response = client.post(path=path, data={"first_name": test_this})
    assert isinstance(response, TemplateResponse)
    assert response.status_code == HTTPStatus.OK
    assert response.template_name == "profiles/tab_personal.html"
    assert test_this in response.rendered_content
    assert test_this == test_user.profile.first_name  # type: ignore


def test_hx_del_user_post(client, sample_user):
    path = reverse("profiles:hx_del_user_post")
    test_user = get_user_model().objects.filter(email=sample_user.email)
    assert test_user.exists()
    client.force_login(sample_user)
    response = client.post(path)
    assert isinstance(response, HttpResponseRedirect)
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == "/"
    assert not test_user.exists()
