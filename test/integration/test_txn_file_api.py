import os

import pytest
from django.urls import reverse
from rest_framework.test import APIClient


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


def test_post_txn_pdf(api_client: APIClient, db):
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    int_test_path = os.path.join(BASE_DIR, "test.pdf")
    with open(int_test_path, "rb") as file:
        post_txn_pdf = reverse("txnfile")
        response = api_client.post(post_txn_pdf, {"file": file}, format="multipart")
    assert response.status_code == 200, f"Error code {response.data}"
