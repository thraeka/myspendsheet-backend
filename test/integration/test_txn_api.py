from copy import deepcopy
from datetime import date
from typing import Any, Dict

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


@pytest.fixture
def txn_case_mod() -> Dict[str, Any]:
    """
    Update to transaction
    """
    return {
        "description": "Test Case 1 Updated",
        "amount": 200.00,
    }


def format_resp_data(resp_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Input response data and format to match original data
    """
    formatted_resp_data = deepcopy(resp_data)
    formatted_resp_data["amount"] = f"{resp_data["amount"]:.2f}"
    formatted_resp_data["date"] = date.today().strftime("%Y-%m-%d")
    formatted_resp_data["date_of_input"] = date.today().strftime("%Y-%m-%d")
    return formatted_resp_data


def test_txn_api(api_client: APIClient, user, txn_case_mod: Dict[str, Any], db):
    """
    Test the txn CRUD API and summary API

    Test:
        1. POST single txn
        2. GET txn from #1
        3. Update txn from #1
        4. POST another single txn
        5. GET summary of txn from db

    Args:
        api_client (APIClient): The API client fixture for making HTTP requests.
        txn_case_mod (Dict[str, Any]): The modifications of test_txn_1
        db: The database fixture for interacting with the test database.
    """

    login = api_client.login(username="testuser", password="password")
    assert login is True
    # Test posting a txn from today to db
    today = date.today()
    before_today = date(2025, 3, 20)
    end_date = today.strftime("%Y-%m-%d")
    start_date = before_today.strftime("%Y-%m-%d")
    test_txn_1 = {
        "date": today,
        "description": "Test Case 1",
        "amount": 100.30,
        "category": "Test",
        "source": "Manual",
        "source_name": "User Input",
        "date_of_input": today,
    }
    url = reverse("txn-list")
    response = api_client.post(url, data=test_txn_1, format="json")

    assert response.status_code == 201, f"Error code: {response.data}"
    assert response.data == {
        "id": 1,
        "date": end_date,
        "description": "Test Case 1",
        "amount": "100.30",
        "category": "Test",
        "source": "Manual",
        "source_name": "User Input",
        "date_of_input": end_date,
    }
    # give test_txn_1 the id assigned by db
    test_txn_1["id"] = response.data["id"]

    # Test updating txn
    update_txn_url = reverse("txn-detail", kwargs={"pk": test_txn_1["id"]})
    response = api_client.patch(update_txn_url, data=txn_case_mod, format="json")
    updated_txn = {**test_txn_1, **txn_case_mod}
    assert response.data == format_resp_data(updated_txn)
    assert response.status_code == 200, f"Error code: {response.data}"

    # Add another test_txn
    test_txn_2 = {
        "date": today,
        "description": "Test Case 2",
        "amount": 123.45,
        "category": "Test2",
        "source": "Manual",
        "source_name": "User Input",
        "date_of_input": today,
    }
    url = reverse("txn-list")
    response = api_client.post(url, data=test_txn_2, format="json")

    assert response.status_code == 201

    # Test getting bulk transactions
    bulk_txn_url = reverse("txn-list")
    response = api_client.get(bulk_txn_url)

    # Test getting the summary data
    summary_url = reverse(
        "summary", kwargs={"start_date": start_date, "end_date": end_date}
    )
    response = api_client.get(summary_url)
    assert response.status_code == 200, f"Error code: {response.data}"
    delete_url = reverse("txn-detail", kwargs={"pk": test_txn_1["id"]})
    response = api_client.delete(delete_url)
    assert response.status_code == 204

    response = api_client.get(delete_url)
    assert response.status_code == 404

    # Test getting the summary data
    summary_url = reverse(
        "summary", kwargs={"start_date": start_date, "end_date": end_date}
    )
    response = api_client.get(summary_url)
    assert response.status_code == 200, f"Error code: {response.data}"
    assert response.data["date_range"] == [start_date, end_date]
    # Convert total by cat amount from str to float, calc sum all cat total
    sum_of_total_by_cat = sum(
        float(amount) for amount in response.data["total_by_cat"].values()
    )
    assert float(response.data["total"]) == sum_of_total_by_cat
