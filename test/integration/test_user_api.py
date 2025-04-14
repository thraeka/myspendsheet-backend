import pytest
from django.urls import reverse
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    return APIClient()


# Test basic user creation
@pytest.mark.django_db
def test_create_user(api_client):
    response = api_client.post(
        reverse("user"), {"username": "hello", "password": "hello"}
    )
    assert response.status_code == 201


# Test for user create with missing/empty inputs
@pytest.mark.django_db
@pytest.mark.parametrize(
    "data",
    [
        {},  # empty username & password
        {"username": "onlyuser"},
        {"password": "onlypass"},
        {"username": "", "password": "emptyuser"},
        {"username": "emptypw", "password": ""},
    ],
)
def test_create_user_missing_fields(api_client, data):
    response = api_client.post(reverse("user"), data)
    assert response.status_code == 400


# Test for creating same user twice
@pytest.mark.django_db
def test_create_user_duplicate(api_client):
    data = {"username": "dupeuser", "password": "pass123"}
    first = api_client.post(reverse("user"), data)
    second = api_client.post(reverse("user"), data)
    assert first.status_code == 201
    assert second.status_code == 400
