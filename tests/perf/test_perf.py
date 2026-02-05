import pytest
import time
import requests
import platform

BASE_URL = "http://localhost:5000"
REQUEST_TIMEOUT = 5.0
PERF_LIMIT = 2.0 if platform.system() == "Windows" else 0.5

def cleanup_all_accounts():
    try:
        r = requests.get(f"{BASE_URL}/api/accounts", timeout=1.0)
        if r.status_code == 200:
            for account in r.json():
                requests.delete(f"{BASE_URL}/api/accounts/{account['pesel']}", timeout=1.0)
    except:
        pass  # Flask might not be running yet

def test_create_and_delete_100_times():
    cleanup_all_accounts()
    try:
        requests.get(f"{BASE_URL}/api/accounts", timeout=2.0)
    except:
        pass

    for i in range(100):
        pesel = f"9001011{i:04d}"  # unique 11-char PESEL per iteration
        payload = {"name": "Perf", "surname": "Test", "pesel": pesel}

        # --- CREATE ---
        start = time.time()
        r_create = requests.post(
            f"{BASE_URL}/api/accounts",
            json=payload,
            timeout=REQUEST_TIMEOUT,
        )
        elapsed_create = time.time() - start

        assert r_create.status_code == 201
        assert elapsed_create < PERF_LIMIT, (
            f"Iteration {i}: CREATE took {elapsed_create:.3f}s (limit {PERF_LIMIT}s)"
        )

        # --- DELETE ---
        start = time.time()
        r_delete = requests.delete(
            f"{BASE_URL}/api/accounts/{pesel}",
            timeout=REQUEST_TIMEOUT,
        )
        elapsed_delete = time.time() - start

        assert r_delete.status_code == 200, (
            f"Iteration {i}: DELETE failed with {r_delete.status_code}"
        )
        assert elapsed_delete < PERF_LIMIT, (
            f"Iteration {i}: DELETE took {elapsed_delete:.3f}s (limit {PERF_LIMIT}s)"
        )


TRANSFER_AMOUNT = 10  # PLN per transfer
NUM_TRANSFERS = 100


def test_create_account_and_100_incoming_transfers():
    cleanup_all_accounts()
    try:
        requests.get(f"{BASE_URL}/api/accounts", timeout=2.0)
    except:
        pass

    pesel = "90010199999"
    payload = {"name": "Perf", "surname": "Transfer", "pesel": pesel}

    # --- CREATE account ---
    start = time.time()
    r_create = requests.post(
        f"{BASE_URL}/api/accounts",
        json=payload,
        timeout=REQUEST_TIMEOUT,
    )
    elapsed = time.time() - start

    assert r_create.status_code == 201, (
        f"CREATE failed with {r_create.status_code}"
    )
    assert elapsed < PERF_LIMIT, (
        f"CREATE took {elapsed:.3f}s (limit {PERF_LIMIT}s)"
    )

    # --- 100 incoming transfers ---
    for i in range(NUM_TRANSFERS):
        start = time.time()
        r_transfer = requests.post(
            f"{BASE_URL}/api/accounts/{pesel}/transfer",
            json={"amount": TRANSFER_AMOUNT, "type": "incoming"},
            timeout=REQUEST_TIMEOUT,
        )
        elapsed = time.time() - start

        assert r_transfer.status_code == 200, (
            f"Transfer {i}: failed with {r_transfer.status_code}"
        )
        assert elapsed < PERF_LIMIT, (
            f"Transfer {i}: took {elapsed:.3f}s (limit {PERF_LIMIT}s)"
        )

    # --- Verify final balance ---
    r_check = requests.get(
        f"{BASE_URL}/api/accounts/{pesel}",
        timeout=REQUEST_TIMEOUT,
    )
    assert r_check.status_code == 200
    expected_balance = NUM_TRANSFERS * TRANSFER_AMOUNT  # 1000
    actual_balance = r_check.get_json()["balance"]
    assert actual_balance == expected_balance, (
        f"Expected balance {expected_balance}, got {actual_balance}"
    )


NUM_BONUS_ACCOUNTS = 1000


def test_create_1000_then_delete_all():
    cleanup_all_accounts()
    try:
        requests.get(f"{BASE_URL}/api/accounts", timeout=2.0)
    except:
        pass

    pesels = []

    # --- Phase 1: CREATE all ---
    for i in range(NUM_BONUS_ACCOUNTS):
        pesel = f"8001011{i:04d}"
        pesels.append(pesel)
        payload = {"name": "Bonus", "surname": "Test", "pesel": pesel}

        start = time.time()
        r = requests.post(
            f"{BASE_URL}/api/accounts",
            json=payload,
            timeout=REQUEST_TIMEOUT,
        )
        elapsed = time.time() - start

        assert r.status_code == 201, (
            f"CREATE {i}: failed with {r.status_code}"
        )
        assert elapsed < PERF_LIMIT, (
            f"CREATE {i}: took {elapsed:.3f}s (limit {PERF_LIMIT}s)"
        )

    # --- Phase 2: DELETE all ---
    for i, pesel in enumerate(pesels):
        start = time.time()
        r = requests.delete(
            f"{BASE_URL}/api/accounts/{pesel}",
            timeout=REQUEST_TIMEOUT,
        )
        elapsed = time.time() - start

        assert r.status_code == 200, (
            f"DELETE {i}: failed with {r.status_code}"
        )
        assert elapsed < PERF_LIMIT, (
            f"DELETE {i}: took {elapsed:.3f}s (limit {PERF_LIMIT}s)"
        )