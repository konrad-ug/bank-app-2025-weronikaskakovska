import subprocess
import time
import requests
import os
import sys


BASE_URL = "http://127.0.0.1:5000"

def start_flask():
    env = os.environ.copy()
    subprocess.Popen(
        [sys.executable, "-m", "flask", "run", "--host=127.0.0.1", "--port=5000"],
        env=env
    )


def wait_for_api():
    for _ in range(60):
        try:
            requests.get(BASE_URL, timeout=0.3)
            return
        except Exception:
            time.sleep(0.2)
    raise RuntimeError("API did not start")


start_flask()
wait_for_api()

def test_create_and_delete_account_100_times():
    for i in range(100):
        payload = {
            "first_name": f"Jan{i}",
            "last_name": "Test",
            "pesel": f"900000000{i}"
        }

        # CREATE
        create_resp = requests.post(
            f"{BASE_URL}/accounts",
            json=payload,
            timeout=0.5
        )

        assert create_resp.status_code == 201
        account_id = create_resp.json()["id"]

        # DELETE
        delete_resp = requests.delete(
            f"{BASE_URL}/accounts/{account_id}",
            timeout=1
        )

        assert delete_resp.status_code == 200


def test_create_account_and_100_incoming_transfers():
    payload = {
        "first_name": "Perf",
        "last_name": "Test",
        "pesel": "80000000000"
    }

    create_resp = requests.post(
        f"{BASE_URL}/accounts",
        json=payload,
        timeout=1
    )

    assert create_resp.status_code == 201
    account_id = create_resp.json()["id"]

    expected_balance = 0

    for i in range(100):
        transfer_payload = {
            "amount": 10
        }

        transfer_resp = requests.post(
            f"{BASE_URL}/accounts/{account_id}/deposit",
            json=transfer_payload,
            timeout=1
        )

        assert transfer_resp.status_code == 200
        expected_balance += 10

    # CHECK BALANCE
    balance_resp = requests.get(
        f"{BASE_URL}/accounts/{account_id}",
        timeout=1
    )

    assert balance_resp.status_code == 200
    assert balance_resp.json()["balance"] == expected_balance
