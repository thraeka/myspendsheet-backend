from datetime import date, timedelta

import pytest
from django.core.cache import cache
from django.urls import reverse
from rest_framework.response import Response
from rest_framework.test import APIClient


####################
# PyTest Fixtures
####################


@pytest.fixture
@pytest.mark.django_db
def client() -> APIClient:
    client = APIClient()
    resp = client.post("/user/", {"username": "test", "password": "test"})
    resp = client.post("/token/", {"username": "test", "password": "test"})
    token = resp.data["access"]
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return client


@pytest.fixture
def start_date() -> str:
    """Start date used throughtout tests"""
    return (date.today() - timedelta(days=7)).isoformat()


@pytest.fixture
def end_date() -> str:
    """End date used throughout tests"""
    return date.today().isoformat()


@pytest.fixture
def txn() -> dict[str, str | float]:
    """Txn data used throughout tests"""
    return {
        "date": date.today().isoformat(),
        "description": "Summary Test",
        "amount": 123.45,
        "category": "Food",
    }


@pytest.fixture(autouse=True)
def clear_cache() -> None:
    """Clear cache btw tests"""
    cache.clear()


####################
# Utility functions
####################


def post_txn(client: APIClient, data: dict) -> Response:
    txn_url = reverse("txn-list")
    return client.post(txn_url, data=data)


def patch_txn(client: APIClient, id: int, data: dict) -> Response:
    txn_patch_url = reverse("txn-detail", kwargs={"pk": id})
    return client.patch(txn_patch_url, data=data)


def delete_txn(client: APIClient, id: int) -> Response:
    delete_url = reverse("txn-detail", kwargs={"pk": id})
    return client.delete(delete_url)


def get_summary(client: APIClient, start_date: str, end_date: str) -> Response:
    past_week_summary_url = reverse("summary", args=[start_date, end_date])
    return client.get(past_week_summary_url)


####################
# Tests
####################


@pytest.mark.django_db
def test_no_txn(client: APIClient, start_date: str, end_date: str) -> None:
    """ Test Case: Nothing in database """
    resp = get_summary(client, start_date, end_date)
    assert resp.status_code == 200
    assert resp.data == {
        "date_range": [start_date, end_date],
        "total": "0.00",
        "total_by_cat": {},
    }


@pytest.mark.django_db
def test_add_txn(client: APIClient, start_date: str, end_date: str, txn: dict) -> None:
    """ Test Case: Adding txn """
    resp = post_txn(client, txn)
    resp = get_summary(client, start_date, end_date)
    assert resp.status_code == 200
    assert resp.data == {
        "date_range": [start_date, end_date],
        "total": "123.45",
        "total_by_cat": {
            "Food": "123.45",
        },
    }


@pytest.mark.django_db
def test_add_rm_txn(
    client: APIClient, start_date: str, end_date: str, txn: dict
) -> None:
    """ Test Case: Adding and removing txn """
    resp = post_txn(client, txn)
    resp = delete_txn(client, resp.data["id"])
    resp = get_summary(client, start_date, end_date)
    assert resp.status_code == 200
    assert resp.data == {
        "date_range": [start_date, end_date],
        "total": "0.00",
        "total_by_cat": {},
    }


@pytest.mark.django_db
def test_txn_cat_change(
    client: APIClient, start_date: str, end_date: str, txn: dict
) -> None:
    """ Test Case: Update txn from one category to next """
    resp = post_txn(client, txn)
    resp = post_txn(client, txn)
    resp = patch_txn(client, resp.data["id"], {"category": "Restaurant"})
    resp = get_summary(client, start_date, end_date)
    assert resp.status_code == 200
    assert resp.data == {
        "date_range": [start_date, end_date],
        "total": "246.90",
        "total_by_cat": {
            "Food": "123.45",
            "Restaurant": "123.45",
        },
    }


@pytest.mark.django_db
def test_txn_out_of_range(
    client: APIClient, start_date: str, end_date: str, txn: dict
) -> None:
    """ Test Case: Txn is out of summary range """
    resp = post_txn(client, txn)
    txn_date = (date.fromisoformat(start_date) - timedelta(days=1)).isoformat()
    resp = patch_txn(client, resp.data["id"], {"date": txn_date})
    resp = get_summary(client, start_date, end_date)
    assert resp.status_code == 200
    assert resp.data == {
        "date_range": [start_date, end_date],
        "total": "0.00",
        "total_by_cat": {},
    }


@pytest.mark.django_db
def test_txn_amt_update(
    client: APIClient, start_date: str, end_date: str, txn: dict
) -> None:
    """ Test Case: Update txn value to higher """
    resp = post_txn(client, txn)
    resp = patch_txn(client, resp.data["id"], {"amount": 543.21})
    resp = get_summary(client, start_date, end_date)
    assert resp.status_code == 200
    assert resp.data == {
        "date_range": [start_date, end_date],
        "total": "543.21",
        "total_by_cat": {
            "Food": "543.21",
        },
    }


@pytest.mark.django_db
def test_two_txn_same_cat(
    client: APIClient, start_date: str, end_date: str, txn: dict
) -> None:
    """ Test Case: Adding two txn of same category """
    resp = post_txn(client, data=txn)
    resp = post_txn(client, data=txn)
    resp = get_summary(client, start_date, end_date)
    assert resp.status_code == 200
    assert resp.data == {
        "date_range": [start_date, end_date],
        "total": "246.90",
        "total_by_cat": {
            "Food": "246.90",
        },
    }


@pytest.mark.django_db
def test_txn_amt_update_less(
    client: APIClient, start_date: str, end_date: str, txn: dict
) -> None:
    """ Test Case: Txn update to lower amt """
    resp = post_txn(client, txn)
    resp = patch_txn(client, resp.data["id"], {"amount": 3.21})
    resp = get_summary(client, start_date, end_date)
    assert resp.status_code == 200
    assert resp.data == {
        "date_range": [start_date, end_date],
        "total": "3.21",
        "total_by_cat": {
            "Food": "3.21",
        },
    }

# TODO: Add test cases which test robustness like invalid inputs