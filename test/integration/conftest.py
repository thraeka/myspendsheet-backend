from datetime import date, timedelta
from typing import Callable, Union

import pytest
from django.core.cache import cache
from integration.int_test_util import random_date
from rest_framework.test import APIClient


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
def txn(start_date: str, end_date: str) -> dict[str, Union[str, float]]:
    """Txn data used throughout tests"""
    return {
        "date": random_date(start_date, end_date),
        "description": "Summary Test",
        "amount": 123.45,
        "category": "Food",
    }


@pytest.fixture
def txn_factory(start_date: str, end_date: str) -> Callable:
    """Txn factory to create txn with diff values"""

    def _make_txn(**kwargs):
        txn = {
            "date": random_date(start_date, end_date),
            "description": "Summary Test",
            "amount": 123.45,
            "category": "Food",
        }
        txn.update(**kwargs)
        return txn

    return _make_txn


@pytest.fixture
def test_dates() -> dict:
    return {
        "today": date.today().isoformat(),
        "yesterday": (date.today() - timedelta(days=1)).isoformat(),
        "week_ago": (date.today() - timedelta(days=7)).isoformat(),
    }


@pytest.fixture(autouse=True)
def clear_cache() -> None:
    """Clear cache btw tests"""
    cache.clear()
