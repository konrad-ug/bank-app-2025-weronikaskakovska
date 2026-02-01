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
    assert r2.status_code == 409
    assert r2.get_json() == {"error": "Pesel already exists"}

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

def test_transfer_incoming_creates_balance(client, sample_account):
    client.post("/api/accounts", json=sample_account)
    r = client.post(
        f"/api/accounts/{sample_account['pesel']}/transfer",
        json={"amount": 500, "type": "incoming"}
    )
    assert r.status_code == 200
    assert r.get_json() == {"message": "Zlecenie przyjęto do realizacji"}
    data = client.get(f"/api/accounts/{sample_account['pesel']}").get_json()
    assert data["balance"] == 500


def test_transfer_outgoing_success(client, sample_account):
    client.post("/api/accounts", json=sample_account)
    # top up
    client.post(f"/api/accounts/{sample_account['pesel']}/transfer", json={"amount": 200, "type": "incoming"})
    r = client.post(
        f"/api/accounts/{sample_account['pesel']}/transfer",
        json={"amount": 150, "type": "outgoing"}
    )
    assert r.status_code == 200
    data = client.get(f"/api/accounts/{sample_account['pesel']}").get_json()
    assert data["balance"] == 50


def test_transfer_outgoing_insufficient_funds(client, sample_account):
    client.post("/api/accounts", json=sample_account)
    r = client.post(
        f"/api/accounts/{sample_account['pesel']}/transfer",
        json={"amount": 50, "type": "outgoing"}
    )
    assert r.status_code == 422
    assert "Za mało" in r.get_json().get("error", "")


def test_transfer_express_success(client, sample_account):
    client.post("/api/accounts", json=sample_account)
    # top up
    client.post(f"/api/accounts/{sample_account['pesel']}/transfer", json={"amount": 100, "type": "incoming"})
    r = client.post(
        f"/api/accounts/{sample_account['pesel']}/transfer",
        json={"amount": 50, "type": "express"}
    )
    assert r.status_code == 200
    data = client.get(f"/api/accounts/{sample_account['pesel']}").get_json()
    # express charges amount + 1 fee
    assert data["balance"] == 49


def test_transfer_unknown_type(client, sample_account):
    client.post("/api/accounts", json=sample_account)
    r = client.post(
        f"/api/accounts/{sample_account['pesel']}/transfer",
        json={"amount": 10, "type": "weird"}
    )
    assert r.status_code == 400
    assert r.get_json() == {"error": "Unknown transfer type"}


def test_transfer_account_not_found(client):
    r = client.post("/api/accounts/99999999999/transfer", json={"amount": 10, "type": "incoming"})
    assert r.status_code == 404

import pytest

def test_patch_account_not_found_returns_json(client):
    # PATCH on non-existent account should return 404 with JSON error
    r = client.patch("/api/accounts/99999999999", json={"name": "Adam"})
    assert r.status_code == 404
    assert r.get_json() == {"error": "Not found"}


def test_patch_invalid_json_returns_400(client, sample_account):
    # create account first
    client.post("/api/accounts", json=sample_account)

    # send non-dict JSON (e.g. a list) -> Invalid JSON
    r = client.patch(f"/api/accounts/{sample_account['pesel']}", json=["invalid"])
    assert r.status_code == 400
    assert r.get_json() == {"error": "Invalid JSON"}


def test_transfer_invalid_json_returns_400(client, sample_account):
    client.post("/api/accounts", json=sample_account)

    r = client.post(
        f"/api/accounts/{sample_account['pesel']}/transfer",
        json=["invalid"]
    )
    assert r.status_code == 400
    assert r.get_json() == {"error": "Invalid JSON"}


def test_transfer_missing_fields_returns_400(client, sample_account):
    client.post("/api/accounts", json=sample_account)

    # missing 'type'
    r = client.post(
        f"/api/accounts/{sample_account['pesel']}/transfer",
        json={"amount": 100}
    )
    assert r.status_code == 400
    assert r.get_json() == {"error": "Missing fields"}

    # missing 'amount'
    r2 = client.post(
        f"/api/accounts/{sample_account['pesel']}/transfer",
        json={"type": "incoming"}
    )
    assert r2.status_code == 400
    assert r2.get_json() == {"error": "Missing fields"}