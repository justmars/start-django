from http import HTTPStatus

import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_contact_url(client):
    response_location = client.get("/contact")
    assert response_location.status_code == HTTPStatus.OK
    assert response_location.request["PATH_INFO"] == "/contact"

    response_pathname = client.get(reverse("pages:contact"))
    assert response_pathname.status_code == HTTPStatus.OK
    assert response_pathname.request["PATH_INFO"] == "/contact"


@pytest.mark.django_db
def test_contact_submit_valid(client, msg):
    res = client.post("/contact", msg)
    assert res.status_code == HTTPStatus.OK


def test_contact_submit_invalid(client, msg):
    res = client.post("/contact", msg | {"email": "john@"})
    assert res.status_code == HTTPStatus.OK
