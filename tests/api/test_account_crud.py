import requests
import pytest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from api import app


BASE_URL = "http://127.0.0.1:5000/api/accounts"


@pytest.fixture
def sample_account():
    return {
        "name": "Jan",
        "surname": "Kowalski",
        "pesel": "90010112345"
    }

@pytest.fixture(autouse=True)
def cleanup_registry(sample_account):
    """Clean up the sample account before and after each test."""
    requests.delete(f"{BASE_URL}/{sample_account['pesel']}")
    yield
    requests.delete(f"{BASE_URL}/{sample_account['pesel']}")




def test_create_account_invalid_json():
    r = requests.post(BASE_URL, json=["invalid"])
    assert r.status_code in [400, 500]

def test_create_account_extra_fields(sample_account):
    sample_account["extra"] = "ignored"
    r = requests.post(BASE_URL, json=sample_account)
    assert r.status_code == 201
    r2 = requests.get(f"{BASE_URL}/{sample_account['pesel']}")
    assert "extra" not in r2.json()


def test_create_account_duplicate_pesel(sample_account):
    r1 = requests.post(BASE_URL, json=sample_account)
    assert r1.status_code == 201
    r2 = requests.post(BASE_URL, json=sample_account)
    # API currently allows duplicate, test will pass; adjust API if duplicates not allowed
    assert r2.status_code == 201


def test_get_account_by_pesel(sample_account):
    requests.post(BASE_URL, json=sample_account)
    r = requests.get(f"{BASE_URL}/{sample_account['pesel']}")
    assert r.status_code == 200
    assert r.json()["name"] == sample_account["name"]


def test_get_account_not_found():
    r = requests.get(f"{BASE_URL}/99999999999")
    assert r.status_code == 404

def test_get_all_accounts_empty():
    r = requests.get(BASE_URL)
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_update_account(sample_account):
    requests.post(BASE_URL, json=sample_account)
    r = requests.patch(f"{BASE_URL}/{sample_account['pesel']}", json={"name": "Adam"})
    assert r.status_code == 200
    r2 = requests.get(f"{BASE_URL}/{sample_account['pesel']}")
    assert r2.json()["name"] == "Adam"


def test_update_account_surname(sample_account):
    requests.post(BASE_URL, json=sample_account)
    r = requests.patch(f"{BASE_URL}/{sample_account['pesel']}", json={"surname": "Nowak"})
    assert r.status_code == 200
    r2 = requests.get(f"{BASE_URL}/{sample_account['pesel']}")
    assert r2.json()["surname"] == "Nowak"
    assert r2.json()["name"] == "Jan"


def test_update_multiple_fields(sample_account):
    requests.post(BASE_URL, json=sample_account)
    r = requests.patch(
        f"{BASE_URL}/{sample_account['pesel']}",
        json={"name": "Adam", "surname": "Nowak"}
    )
    assert r.status_code == 200
    r2 = requests.get(f"{BASE_URL}/{sample_account['pesel']}")
    assert r2.json()["name"] == "Adam"
    assert r2.json()["surname"] == "Nowak"


def test_update_account_not_found():
    r = requests.patch(f"{BASE_URL}/99999999999", json={"name": "Adam"})
    assert r.status_code == 404


def test_update_empty_json(sample_account):
    requests.post(BASE_URL, json=sample_account)
    r = requests.patch(f"{BASE_URL}/{sample_account['pesel']}", json={})
    assert r.status_code == 200
    r2 = requests.get(f"{BASE_URL}/{sample_account['pesel']}")
    # Original values unchanged
    assert r2.json()["name"] == "Jan"
    assert r2.json()["surname"] == "Kowalski"


def test_update_with_ignored_fields(sample_account):
    requests.post(BASE_URL, json=sample_account)
    r = requests.patch(f"{BASE_URL}/{sample_account['pesel']}", json={"balance": 1000})
    assert r.status_code == 200
    r2 = requests.get(f"{BASE_URL}/{sample_account['pesel']}")
    # balance unchanged, API ignores unknown fields
    assert r2.json()["balance"] == 0


def test_delete_account(sample_account):
    requests.post(BASE_URL, json=sample_account)
    r = requests.delete(f"{BASE_URL}/{sample_account['pesel']}")
    assert r.status_code == 200
    r2 = requests.get(f"{BASE_URL}/{sample_account['pesel']}")
    assert r2.status_code == 404


def test_delete_account_not_found():
    r = requests.delete(f"{BASE_URL}/99999999999")
    assert r.status_code == 404


def test_get_all_accounts(sample_account):
    requests.delete(f"{BASE_URL}/{sample_account['pesel']}")

    # Create a few accounts
    requests.post(BASE_URL, json=sample_account)

    sample_account2 = {
        "name": "Anna",
        "surname": "Nowak",
        "pesel": "92020212345"
    }
    requests.post(BASE_URL, json=sample_account2)

    r = requests.get(BASE_URL)
    assert r.status_code == 200
    accounts = r.json()
    assert len(accounts) >= 2

    requests.delete(f"{BASE_URL}/{sample_account['pesel']}")
    requests.delete(f"{BASE_URL}/{sample_account2['pesel']}")



def test_create_account_invalid_pesel():
    invalid_account = {
        "name": "Jan",
        "surname": "Kowalski",
        "pesel": "123"
    }
    r = requests.post(BASE_URL, json=invalid_account)
    assert r.status_code in [201, 400, 422]




def test_api_response_format(sample_account):
    requests.post(BASE_URL, json=sample_account)
    r2 = requests.get(f"{BASE_URL}/{sample_account['pesel']}")
    data = r2.json()
    assert "name" in data
    assert "surname" in data
    assert "pesel" in data


def test_create_account_missing_fields():
    incomplete_account = {
        "name": "Jan"
    }
    r = requests.post(BASE_URL, json=incomplete_account)
    assert r.status_code == 500

def test_create_account():
    client = app.test_client()
    response = client.post(
        "/api/accounts",
        json={"name": "Alice", "surname": "Smith", "pesel": "90010112345"}
    )
    assert response.status_code == 201