import pytest


@pytest.fixture
def sample_account():
    return {
        "name": "Jan",
        "surname": "Kowalski",
        "pesel": "90010112345"
    }


def test_create_account(client, sample_account):
    r = client.post("/api/accounts", json=sample_account)
    assert r.status_code == 201


def test_create_account_invalid_json(client):
    r = client.post("/api/accounts", json=["invalid"])
    assert r.status_code == 400


def test_create_account_missing_fields(client):
    r = client.post("/api/accounts", json={"name": "Jan"})
    assert r.status_code == 400


def test_create_account_extra_fields(client, sample_account):
    sample_account["extra"] = "ignored"
    r = client.post("/api/accounts", json=sample_account)
    assert r.status_code == 201

    r2 = client.get(f"/api/accounts/{sample_account['pesel']}")
    data = r2.get_json()
    assert "extra" not in data


def test_create_account_duplicate_pesel(client, sample_account):
    r1 = client.post("/api/accounts", json=sample_account)
    assert r1.status_code == 201

    r2 = client.post("/api/accounts", json=sample_account)
    # API currently allows duplicates
    assert r2.status_code == 201


def test_get_account_by_pesel(client, sample_account):
    client.post("/api/accounts", json=sample_account)

    r = client.get(f"/api/accounts/{sample_account['pesel']}")
    assert r.status_code == 200
    assert r.get_json()["name"] == "Jan"


def test_get_account_not_found(client):
    r = client.get("/api/accounts/99999999999")
    assert r.status_code == 404


def test_get_all_accounts_empty(client):
    r = client.get("/api/accounts")
    assert r.status_code == 200
    assert isinstance(r.get_json(), list)


def test_get_all_accounts(client, sample_account):
    client.post("/api/accounts", json=sample_account)

    second_account = {
        "name": "Anna",
        "surname": "Nowak",
        "pesel": "92020212345"
    }
    client.post("/api/accounts", json=second_account)

    r = client.get("/api/accounts")
    accounts = r.get_json()

    assert r.status_code == 200
    assert len(accounts) == 2


def test_update_account_name(client, sample_account):
    client.post("/api/accounts", json=sample_account)

    r = client.patch(
        f"/api/accounts/{sample_account['pesel']}",
        json={"name": "Adam"}
    )
    assert r.status_code == 200

    r2 = client.get(f"/api/accounts/{sample_account['pesel']}")
    assert r2.get_json()["name"] == "Adam"


def test_update_account_surname(client, sample_account):
    client.post("/api/accounts", json=sample_account)

    r = client.patch(
        f"/api/accounts/{sample_account['pesel']}",
        json={"surname": "Nowak"}
    )
    assert r.status_code == 200

    data = client.get(
        f"/api/accounts/{sample_account['pesel']}"
    ).get_json()

    assert data["name"] == "Jan"
    assert data["surname"] == "Nowak"


def test_update_multiple_fields(client, sample_account):
    client.post("/api/accounts", json=sample_account)

    r = client.patch(
        f"/api/accounts/{sample_account['pesel']}",
        json={"name": "Adam", "surname": "Nowak"}
    )
    assert r.status_code == 200

    data = client.get(
        f"/api/accounts/{sample_account['pesel']}"
    ).get_json()

    assert data["name"] == "Adam"
    assert data["surname"] == "Nowak"


def test_update_account_not_found(client):
    r = client.patch(
        "/api/accounts/99999999999",
        json={"name": "Adam"}
    )
    assert r.status_code == 404


def test_update_empty_json(client, sample_account):
    client.post("/api/accounts", json=sample_account)

    r = client.patch(
        f"/api/accounts/{sample_account['pesel']}",
        json={}
    )
    assert r.status_code == 200

    data = client.get(
        f"/api/accounts/{sample_account['pesel']}"
    ).get_json()

    assert data["name"] == "Jan"
    assert data["surname"] == "Kowalski"


def test_update_with_ignored_fields(client, sample_account):
    client.post("/api/accounts", json=sample_account)

    r = client.patch(
        f"/api/accounts/{sample_account['pesel']}",
        json={"balance": 9999}
    )
    assert r.status_code == 200

    data = client.get(
        f"/api/accounts/{sample_account['pesel']}"
    ).get_json()

    assert data["balance"] == 0


def test_delete_account(client, sample_account):
    client.post("/api/accounts", json=sample_account)

    r = client.delete(f"/api/accounts/{sample_account['pesel']}")
    assert r.status_code == 200

    r2 = client.get(f"/api/accounts/{sample_account['pesel']}")
    assert r2.status_code == 404


def test_delete_account_not_found(client):
    r = client.delete("/api/accounts/99999999999")
    assert r.status_code == 404


def test_api_response_format(client, sample_account):
    client.post("/api/accounts", json=sample_account)

    data = client.get(
        f"/api/accounts/{sample_account['pesel']}"
    ).get_json()

    assert "name" in data
    assert "surname" in data
    assert "pesel" in data
    assert "balance" in data

def test_get_count_endpoint(client, sample_account):
    # create two accounts via the API (matches style of your other tests)
    client.post("/api/accounts", json=sample_account)

    second_account = {
        "name": "Anna",
        "surname": "Nowak",
        "pesel": "92020212345"
    }
    client.post("/api/accounts", json=second_account)

    r = client.get("/api/accounts/count")
    assert r.status_code == 200
    assert r.get_json() == {"count": 2}