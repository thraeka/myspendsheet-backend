import os

import pytest
from django.urls import reverse
from rest_framework.test import APIClient


@pytest.fixture
def api_client() -> APIClient:
    """
    Fixture to provide a reusable API client for making HTTP requests.

    Returns:
        APIClient: An instance of the Django REST framework test client.
    """
    return APIClient()


def test_post_txn_pdf(api_client: APIClient, db):
    """
    Test the endpoint for uploading a txn PDF (bank statement) and retrieving the parsed txn.

    This test uploads a sample PDF file and then queries the transaction list endpoint to ensure
    that the uploaded transactions are successfully stored and can be retrieved.

    Args:
        api_client (APIClient): The API client fixture for making HTTP requests.
        db: The database fixture for interacting with the test database.
    """
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    int_test_path = os.path.join(BASE_DIR, "test.pdf")
    with open(int_test_path, "rb") as file:
        post_txn_pdf = reverse("txnfile")
        response = api_client.post(post_txn_pdf, {"file": file}, format="multipart")
    assert response.status_code == 200, f"Error code {response.data}"
    date_txn_pdf = reverse("txn-list") + "?date__gte=2025-01-10&date__lte=2025-01-20"
    response = api_client.get(date_txn_pdf)
    assert response.status_code == 200, f"Error code: {response.data}"
