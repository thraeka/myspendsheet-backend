from typing import Callable

import pytest
from django.urls import reverse
from integration.int_test_util import post_txn
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db


def test_no_auth(client: APIClient, txn: dict) -> None:
    """Test Case: No auth"""
    client.credentials()
    resp = post_txn(client, txn)
    assert resp.status_code == 401


def test_filter_exact_amt(client: APIClient, txn_factory: Callable) -> None:
    """Test Case: Filter by exact amount"""
    target_amt = 500.00
    resp = post_txn(client, txn_factory(amount=target_amt, description="Test"))
    resp = post_txn(client, txn_factory(amount=123.46))
    resp = post_txn(client, txn_factory(amount=target_amt, category="Test"))
    exact_amt_filter_url = reverse("txn-list") + f"?amount={target_amt}"
    resp = client.get(exact_amt_filter_url)
    assert resp.status_code == 200
    assert all(float(data["amount"]) == target_amt for data in resp.data)
    assert len(resp.data) == 2


def test_filter_gte_amt(client: APIClient, txn_factory: Callable) -> None:
    """Test Case: Filter by greater than or equal to amount"""
    gte_amt = 500
    resp = post_txn(client, txn_factory(amount=100.00))
    resp = post_txn(client, txn_factory(amount=gte_amt))
    resp = post_txn(client, txn_factory(amount=1000.00))
    exact_amt_filter_url = reverse("txn-list") + f"?amount__gte={gte_amt}"
    resp = client.get(exact_amt_filter_url)
    assert resp.status_code == 200
    assert all(float(data["amount"]) >= gte_amt for data in resp.data)
    assert len(resp.data) == 2


def test_filter_lte_amt(client: APIClient, txn_factory: dict) -> None:
    """Test Case: Filter by less than amount"""
    lte_amt = 500.00
    resp = post_txn(client, txn_factory(amount=100.00))
    resp = post_txn(client, txn_factory(amount=lte_amt))
    resp = post_txn(client, txn_factory(amount=1000.00))
    exact_amt_filter_url = reverse("txn-list") + f"?amount__lte={lte_amt}"
    resp = client.get(exact_amt_filter_url)
    assert resp.status_code == 200
    assert all(float(data["amount"]) <= lte_amt for data in resp.data)
    assert len(resp.data) == 2


def test_filter_exact_date(
    client: APIClient, txn_factory: Callable, test_dates: dict
) -> None:
    """Test Case: Filter by exact date"""
    resp = post_txn(client, txn_factory(date=test_dates["today"]))
    resp = post_txn(client, txn_factory(date=test_dates["yesterday"]))
    resp = post_txn(client, txn_factory(date=test_dates["yesterday"], amount=1.00))
    resp = post_txn(client, txn_factory(date=test_dates["week_ago"]))
    exact_date_filter_url = reverse("txn-list") + f"?date={test_dates["yesterday"]}"
    resp = client.get(exact_date_filter_url)
    assert resp.status_code == 200
    assert all(test_dates["yesterday"] == data["date"] for data in resp.data)
    assert len(resp.data) == 2


def test_filter_gte_date(
    client: APIClient, txn_factory: Callable, test_dates: dict
) -> None:
    """Test Case: Filter by greater date"""
    resp = post_txn(client, txn_factory(date=test_dates["today"]))
    resp = post_txn(client, txn_factory(date=test_dates["today"]))
    resp = post_txn(client, txn_factory(date=test_dates["yesterday"]))
    resp = post_txn(client, txn_factory(date=test_dates["week_ago"]))
    gte_date_url = reverse("txn-list") + f"?date__gte={test_dates["yesterday"]}"
    resp = client.get(gte_date_url)
    assert resp.status_code == 200
    assert all(test_dates["yesterday"] <= data["date"] for data in resp.data)
    assert len(resp.data) == 3


def test_filter_lte_date(
    client: APIClient, txn_factory: Callable, test_dates: dict
) -> None:
    """Test Case: Filter by less than date"""
    resp = post_txn(client, txn_factory(date=test_dates["today"]))
    resp = post_txn(client, txn_factory(date=test_dates["today"]))
    resp = post_txn(client, txn_factory(date=test_dates["yesterday"]))
    resp = post_txn(client, txn_factory(date=test_dates["week_ago"]))
    lte_date_url = reverse("txn-list") + f"?date__lte={test_dates["yesterday"]}"
    resp = client.get(lte_date_url)
    assert resp.status_code == 200
    assert all(test_dates["yesterday"] >= data["date"] for data in resp.data)
    assert len(resp.data) == 2


def test_filter_asc_amt(client: APIClient, txn_factory: Callable) -> None:
    """Test Case: Order by amount ascending"""
    resp = post_txn(client, txn_factory(amount=1.00))
    resp = post_txn(client, txn_factory(amount=1.00))
    resp = post_txn(client, txn_factory(amount=2.10))
    resp = post_txn(client, txn_factory(amount=3.21))
    asc_amt_url = reverse("txn-list") + "?ordering=amount"
    resp = client.get(asc_amt_url)
    assert resp.status_code == 200
    last = float("-inf")
    for data in resp.data:
        cur = float(data["amount"])
        assert cur >= last
        last = cur


def test_filter_desc_amt(client: APIClient, txn_factory: Callable) -> None:
    """Test Case: Order by amount descending"""
    resp = post_txn(client, txn_factory(amount=1.00))
    resp = post_txn(client, txn_factory(amount=1.00))
    resp = post_txn(client, txn_factory(amount=2.10))
    resp = post_txn(client, txn_factory(amount=3.21))
    desc_amt_url = reverse("txn-list") + "?ordering=-amount"
    resp = client.get(desc_amt_url)
    assert resp.status_code == 200
    last = float("inf")
    for data in resp.data:
        cur = float(data["amount"])
        assert cur <= last
        last = cur


def test_filter_asc_date(
    client: APIClient, txn_factory: Callable, test_dates: dict
) -> None:
    """Test Case: Order by date ascending"""
    resp = post_txn(client, txn_factory(date=test_dates["today"]))
    resp = post_txn(client, txn_factory(date=test_dates["today"]))
    resp = post_txn(client, txn_factory(date=test_dates["yesterday"]))
    resp = post_txn(client, txn_factory(date=test_dates["week_ago"]))
    asc_date_url = reverse("txn-list") + "?ordering=date"
    resp = client.get(asc_date_url)
    assert resp.status_code == 200
    last = "0000-00-00"
    for data in resp.data:
        cur = data["date"]
        assert cur >= last
        last = cur


def test_filter_desc_date(
    client: APIClient, txn_factory: Callable, test_dates: dict
) -> None:
    """Test Case: Order by date descending"""
    resp = post_txn(client, txn_factory(date=test_dates["today"]))
    resp = post_txn(client, txn_factory(date=test_dates["today"]))
    resp = post_txn(client, txn_factory(date=test_dates["yesterday"]))
    resp = post_txn(client, txn_factory(date=test_dates["week_ago"]))
    desc_date_url = reverse("txn-list") + "?ordering=-date"
    resp = client.get(desc_date_url)
    assert resp.status_code == 200
    last = test_dates["today"]
    for data in resp.data:
        cur = data["date"]
        assert cur <= last
        last = cur
