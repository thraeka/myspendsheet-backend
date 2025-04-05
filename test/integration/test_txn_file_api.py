import os
from datetime import datetime

import pytest
from django.contrib.auth.models import User
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


@pytest.fixture
def user(db):
    return User.objects.create_user(username="testuser", password="password")


def test_post_txn_pdf(api_client: APIClient, user, db):
    """
    Test the endpoint for uploading a txn PDF (bank statement) and retrieving the parsed txn.

    This test uploads a sample PDF file and then queries the transaction list endpoint to ensure
    that the uploaded transactions are successfully stored and can be retrieved.

    Args:
        api_client (APIClient): The API client fixture for making HTTP requests.
        db: The database fixture for interacting with the test database.
    """
    signup_url = reverse("signup")
    user_info = {"username": "test", "password": "password"}
    response = api_client.post(signup_url, data=user_info, format="json")
    assert response.status_code == 201, f"Error code: {response.data}"

    login = api_client.login(username="testuser", password="password")
    assert login is True

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    # Test post txn file
    int_test_path = os.path.join(BASE_DIR, "test.pdf")
    with open(int_test_path, "rb") as file:
        post_txn_pdf = reverse("txnfile")
        response = api_client.post(post_txn_pdf, {"file": file}, format="multipart")
    assert response.status_code == 200, f"Error code {response.data}"

    # Test get txn with filter
    date_txn_pdf = reverse("txn-list") + "?date__gte=2025-01-10&date__lte=2025-01-20"
    response = api_client.get(date_txn_pdf)
    assert response.status_code == 200, f"Error code: {response.data}"

    # Test getting summary data from specific date range
    start_date = datetime.strptime("2025-01-10", "%Y-%m-%d").date()
    end_date = datetime.strptime("2025-01-20", "%Y-%m-%d").date()
    summary_url = reverse(
        "summary", kwargs={"start_date": start_date, "end_date": end_date}
    )
    response = api_client.get(summary_url)
    assert response.status_code == 200, f"Error code: {response.data}"
    assert response.data["date_range"] == ["2025-01-10", "2025-01-20"]
    assert response.data["total"] == "1044.23"
    sum_of_total_by_cat = sum(
        float(amount) for amount in response.data["total_by_cat"].values()
    )
    assert float(response.data["total"]) == sum_of_total_by_cat
