import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from datetime import date
from typing import Dict, Any
from copy import deepcopy


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


@pytest.fixture
def txn_case() -> Dict[str, Any]:
    dateToday = date.today()
    return {
            "date": dateToday,
            "description": "Test Case 1",
            "amount": 100.30,
            "category": "Test",
            "source": "Manual",
            "source_name": "User Input",
            "date_of_input": dateToday,
            }


@pytest.fixture
def txn_case_mod() -> Dict[str, Any]:
    return {
        "description": "Test Case 1 Updated",
        "amount": 200.00,
    }


@pytest.fixture
def create_txn(api_client: APIClient, txn_case: Dict[str, Any], db) -> Dict[str, Any]:
    url = reverse('txn')
    response = api_client.post(url, data=txn_case, format='json')
    txn_case['id'] = response.data['id']
    return txn_case


def format_resp_data(resp_data: Dict[str, Any]) -> Dict[str, Any]:
    formatted_resp_data = deepcopy(resp_data)
    formatted_resp_data["amount"] = f"{resp_data["amount"]:.2f}"
    formatted_resp_data['date'] = date.today().strftime('%Y-%m-%d')
    formatted_resp_data['date_of_input'] = date.today().strftime('%Y-%m-%d')
    return formatted_resp_data


def test_create_txn(api_client: APIClient, txn_case: Dict[str, Any], db):
    create_txn_url = reverse('txn')
    response = api_client.post(create_txn_url, data=txn_case, format='json')
    txn_case['id'] = response.data['id']

    assert response.data == format_resp_data(txn_case)
    assert response.status_code == 200, f'Error code: {response.data}'


def test_update_txn(api_client: APIClient, create_txn: Dict[str, Any],
                    txn_case_mod: Dict[str, Any], db):
    update_txn_url = reverse('txn_mod', kwargs={'pk': create_txn['id']})
    response = api_client.put(update_txn_url, data=txn_case_mod,
                              format='json')
    updated_txn = {**create_txn, **txn_case_mod}
    assert response.data == format_resp_data(updated_txn)
    assert response.status_code == 200, f'Error code: {response.data}'


def test_delete_txn(api_client: APIClient, create_txn: Dict[str, Any], db):
    delete_url = reverse('txn_mod', kwargs={'pk': create_txn['id']})
    response = api_client.delete(delete_url)

    assert response.status_code == 204
    response = api_client.get(delete_url)
    assert response.status_code == 404
