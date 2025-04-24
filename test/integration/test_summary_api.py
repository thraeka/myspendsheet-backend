from datetime import date, timedelta

import pytest
from integration.int_test_util import delete_txn, get_summary, patch_txn, post_txn
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db


def test_no_txn(client: APIClient, start_date: str, end_date: str) -> None:
    """Test Case: Nothing in database"""
    resp = get_summary(client, start_date, end_date)
    assert resp.status_code == 200
    assert resp.data == {
        "date_range": [start_date, end_date],
        "total": "0.00",
        "total_by_cat": {},
    }


def test_add_txn(client: APIClient, start_date: str, end_date: str, txn: dict) -> None:
    """Test Case: Adding txn"""
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


def test_add_rm_txn(
    client: APIClient, start_date: str, end_date: str, txn: dict
) -> None:
    """Test Case: Adding and removing txn"""
    resp = post_txn(client, txn)
    resp = delete_txn(client, resp.data["id"])
    resp = get_summary(client, start_date, end_date)
    assert resp.status_code == 200
    assert resp.data == {
        "date_range": [start_date, end_date],
        "total": "0.00",
        "total_by_cat": {},
    }


def test_txn_cat_change(
    client: APIClient, start_date: str, end_date: str, txn: dict
) -> None:
    """Test Case: Update txn from one category to next"""
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


def test_txn_out_of_range(
    client: APIClient, start_date: str, end_date: str, txn: dict
) -> None:
    """Test Case: Txn is out of summary range"""
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


def test_txn_amt_update(
    client: APIClient, start_date: str, end_date: str, txn: dict
) -> None:
    """Test Case: Update txn value to higher"""
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


def test_two_txn_same_cat(
    client: APIClient, start_date: str, end_date: str, txn: dict
) -> None:
    """Test Case: Adding two txn of same category"""
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


def test_txn_amt_update_less(
    client: APIClient, start_date: str, end_date: str, txn: dict
) -> None:
    """Test Case: Txn update to lower amt"""
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
