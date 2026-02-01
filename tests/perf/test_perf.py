import pytest
import time
import requests

BASE_URL = "http://localhost:5000"
TIMEOUT = 0.5  # max seconds per request


# ──────────────────────────────────────────────
# Test 1: Create + Delete cycle × 100
# ──────────────────────────────────────────────
def test_create_and_delete_100_times():
    """
    Creates and immediately deletes an account 100 times.
    Every single request must respond in under 0.5 s.
    """
    for i in range(100):
        pesel = f"9001011{i:04d}"  # unique 11-char PESEL per iteration
        payload = {"name": "Perf", "surname": "Test", "pesel": pesel}

        # --- CREATE ---
        start = time.time()
        r_create = requests.post(
            f"{BASE_URL}/api/accounts",
            json=payload,
            timeout=TIMEOUT,
        )
        elapsed_create = time.time() - start

        assert r_create.status_code == 201, (
            f"Iteration {i}: CREATE failed with {r_create.status_code}"
        )
        assert elapsed_create < TIMEOUT, (
            f"Iteration {i}: CREATE took {elapsed_create:.3f}s (limit {TIMEOUT}s)"
        )

        # --- DELETE ---
        start = time.time()
        r_delete = requests.delete(
            f"{BASE_URL}/api/accounts/{pesel}",
            timeout=TIMEOUT,
        )
        elapsed_delete = time.time() - start

        assert r_delete.status_code == 200, (
            f"Iteration {i}: DELETE failed with {r_delete.status_code}"
        )
        assert elapsed_delete < TIMEOUT, (
            f"Iteration {i}: DELETE took {elapsed_delete:.3f}s (limit {TIMEOUT}s)"
        )


# ──────────────────────────────────────────────
# Test 2: Create account + 100 incoming transfers
# ──────────────────────────────────────────────
TRANSFER_AMOUNT = 10  # PLN per transfer
NUM_TRANSFERS = 100


def test_create_account_and_100_incoming_transfers():
    """
    Creates one account, then posts 100 incoming transfers of 10 PLN each.
    Every request must respond in under 0.5 s.
    Final balance must equal 100 × 10 = 1000 PLN.
    """
    pesel = "90010199999"
    payload = {"name": "Perf", "surname": "Transfer", "pesel": pesel}

    # --- CREATE account ---
    start = time.time()
    r_create = requests.post(
        f"{BASE_URL}/api/accounts",
        json=payload,
        timeout=TIMEOUT,
    )
    elapsed = time.time() - start

    assert r_create.status_code == 201, (
        f"CREATE failed with {r_create.status_code}"
    )
    assert elapsed < TIMEOUT, (
        f"CREATE took {elapsed:.3f}s (limit {TIMEOUT}s)"
    )

    # --- 100 incoming transfers ---
    for i in range(NUM_TRANSFERS):
        start = time.time()
        r_transfer = requests.post(
            f"{BASE_URL}/api/accounts/{pesel}/transfer",
            json={"amount": TRANSFER_AMOUNT, "type": "incoming"},
            timeout=TIMEOUT,
        )
        elapsed = time.time() - start

        assert r_transfer.status_code == 200, (
            f"Transfer {i}: failed with {r_transfer.status_code}"
        )
        assert elapsed < TIMEOUT, (
            f"Transfer {i}: took {elapsed:.3f}s (limit {TIMEOUT}s)"
        )

    # --- Verify final balance ---
    r_check = requests.get(
        f"{BASE_URL}/api/accounts/{pesel}",
        timeout=TIMEOUT,
    )
    assert r_check.status_code == 200
    expected_balance = NUM_TRANSFERS * TRANSFER_AMOUNT  # 1000
    actual_balance = r_check.get_json()["balance"]
    assert actual_balance == expected_balance, (
        f"Expected balance {expected_balance}, got {actual_balance}"
    )


# ──────────────────────────────────────────────
# BONUS: Create 1000 accounts, then delete all
# ──────────────────────────────────────────────
NUM_BONUS_ACCOUNTS = 1000


def test_create_1000_then_delete_all():
    """
    Phase 1 – creates 1000 accounts (every request < 0.5 s).
    Phase 2 – deletes all 1000 accounts (every request < 0.5 s).

    Key difference vs. the create-delete loop above:
    the registry grows to 1000 entries before any deletion starts,
    so find/delete operations run against a much larger in-memory list.
    This can expose O(n) performance degradation that the interleaved
    test would never catch.
    """
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
            timeout=TIMEOUT,
        )
        elapsed = time.time() - start

        assert r.status_code == 201, (
            f"CREATE {i}: failed with {r.status_code}"
        )
        assert elapsed < TIMEOUT, (
            f"CREATE {i}: took {elapsed:.3f}s (limit {TIMEOUT}s)"
        )

    # --- Phase 2: DELETE all ---
    for i, pesel in enumerate(pesels):
        start = time.time()
        r = requests.delete(
            f"{BASE_URL}/api/accounts/{pesel}",
            timeout=TIMEOUT,
        )
        elapsed = time.time() - start

        assert r.status_code == 200, (
            f"DELETE {i}: failed with {r.status_code}"
        )
        assert elapsed < TIMEOUT, (
            f"DELETE {i}: took {elapsed:.3f}s (limit {TIMEOUT}s)"
        )