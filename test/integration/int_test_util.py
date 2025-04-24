from datetime import date, timedelta
from random import randint

from django.urls import reverse
from rest_framework.response import Response
from rest_framework.test import APIClient


def post_txn(client: APIClient, data: dict) -> Response:
    """Post client txn"""
    txn_url = reverse("txn-list")
    return client.post(txn_url, data=data)


def patch_txn(client: APIClient, id: int, data: dict) -> Response:
    """Patch client txn by providing id"""
    txn_patch_url = reverse("txn-detail", kwargs={"pk": id})
    return client.patch(txn_patch_url, data=data)


def delete_txn(client: APIClient, id: int) -> Response:
    """Delete client txn by providing id"""
    delete_url = reverse("txn-detail", kwargs={"pk": id})
    return client.delete(delete_url)


def get_summary(client: APIClient, start_date: str, end_date: str) -> Response:
    """Get client summary for date range"""
    past_week_summary_url = reverse("summary", args=[start_date, end_date])
    return client.get(past_week_summary_url)


def random_date(start_date: str, end_date: str) -> str:
    """Random date seven days before date"""
    date_range = (date.fromisoformat(end_date) - date.fromisoformat(start_date)).days
    days = randint(0, date_range)
    return (date.fromisoformat(end_date) - timedelta(days=days)).isoformat()
