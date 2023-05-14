from http import HTTPStatus

import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_about_url(client):
    response_location = client.get("/popular")
    assert response_location.status_code == HTTPStatus.OK
    assert response_location.request["PATH_INFO"] == "/popular"

    response_pathname = client.get(reverse("pages:popular"))
    assert response_pathname.status_code == HTTPStatus.OK
    assert response_pathname.request["PATH_INFO"] == "/popular"
