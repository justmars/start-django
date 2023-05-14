from http import HTTPStatus

import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_home_url(client):
    response_location = client.get("/")
    assert response_location.status_code == HTTPStatus.OK
    assert response_location.request["PATH_INFO"] == "/"

    response_pathname = client.get(reverse("pages:home"))
    assert response_pathname.status_code == HTTPStatus.OK
    assert response_pathname.request["PATH_INFO"] == "/"
