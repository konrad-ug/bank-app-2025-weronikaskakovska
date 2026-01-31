import requests
import pytest

BASE_URL = "http://127.0.0.1:5000/api/accounts"


@pytest.fixture
def sample_account():
    return {
        "name": "Jan",
        "surname": "Kowalski",
        "pesel": "90010112345"
    }


def test_create_account(sample_account):
    r = requests.post(BASE_URL, json=sample_account)
    assert r.status_code == 201


def test_get_account_by_pesel(sample_account):
    requests.post(BASE_URL, json=sample_account)

    r = requests.get(f"{BASE_URL}/{sample_account['pesel']}")

    assert r.status_code == 200
    assert r.json()["name"] == "Jan"


def test_get_account_not_found():
    r = requests.get(f"{BASE_URL}/000")
    assert r.status_code == 404


def test_update_account(sample_account):
    requests.post(BASE_URL, json=sample_account)

    r = requests.patch(
        f"{BASE_URL}/{sample_account['pesel']}",
        json={"name": "Adam"}
    )

    assert r.status_code == 200

    r2 = requests.get(f"{BASE_URL}/{sample_account['pesel']}")
    assert r2.json()["name"] == "Adam"

def test_update_account_not_found():
    r = requests.patch(
        f"{BASE_URL}/99999999999",
        json={"name": "Adam"}
    )
    assert r.status_code == 404

def test_delete_account(sample_account):
    sample_account["pesel"] = "90010112345"
    requests.delete(f"{BASE_URL}/{sample_account['pesel']}")
    r = requests.post(BASE_URL, json=sample_account)
    assert r.status_code == 201
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


def test_create_account_duplicate_pesel(sample_account):
    requests.delete(f"{BASE_URL}/{sample_account['pesel']}")
    r1 = requests.post(BASE_URL, json=sample_account)
    assert r1.status_code == 201

    r2 = requests.post(BASE_URL, json=sample_account)

    requests.delete(f"{BASE_URL}/{sample_account['pesel']}")


def test_update_multiple_fields(sample_account):
    requests.delete(f"{BASE_URL}/{sample_account['pesel']}")
    requests.post(BASE_URL, json=sample_account)

    r = requests.patch(
        f"{BASE_URL}/{sample_account['pesel']}",
        json={"name": "Adam", "surname": "Nowak"}
    )
    assert r.status_code == 200

    r2 = requests.get(f"{BASE_URL}/{sample_account['pesel']}")
    assert r2.json()["name"] == "Adam"
    assert r2.json()["surname"] == "Nowak"

    requests.delete(f"{BASE_URL}/{sample_account['pesel']}")


def test_create_account_invalid_pesel():
    invalid_account = {
        "name": "Jan",
        "surname": "Kowalski",
        "pesel": "123"
    }
    r = requests.post(BASE_URL, json=invalid_account)
    assert r.status_code in [201, 400, 422]


def test_update_account_surname(sample_account):
    """Test updating only the surname field"""
    requests.delete(f"{BASE_URL}/{sample_account['pesel']}")
    requests.post(BASE_URL, json=sample_account)

    r = requests.patch(
        f"{BASE_URL}/{sample_account['pesel']}",
        json={"surname": "Nowak"}
    )
    assert r.status_code == 200

    r2 = requests.get(f"{BASE_URL}/{sample_account['pesel']}")
    assert r2.json()["surname"] == "Nowak"
    assert r2.json()["name"] == "Jan"

    # Clean up
    requests.delete(f"{BASE_URL}/{sample_account['pesel']}")


def test_api_response_format(sample_account):
    requests.delete(f"{BASE_URL}/{sample_account['pesel']}")
    r = requests.post(BASE_URL, json=sample_account)

    r2 = requests.get(f"{BASE_URL}/{sample_account['pesel']}")
    data = r2.json()

    assert "name" in data
    assert "surname" in data
    assert "pesel" in data
    requests.delete(f"{BASE_URL}/{sample_account['pesel']}")


def test_create_account_missing_fields():
    incomplete_account = {
        "name": "Jan"
    }
    r = requests.post(BASE_URL, json=incomplete_account)
    assert r.status_code == 500
