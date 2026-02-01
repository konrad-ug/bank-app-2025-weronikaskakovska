import pytest
import requests
import time

BASE_URL = "http://localhost:5000/api"

class TestAccountPerformance:

    def test_create_delete_account_100_times(self):
        timeout = 0.5
        iterations = 100

        for i in range(iterations):
            # Generuj unikalny PESEL (11 cyfr)
            pesel = f"{90000000000 + i:011d}"

            account_data = {
                "first_name": f"Jan{i}",
                "last_name": "Test",
                "pesel": pesel
            }

            # Tworzenie konta
            start_time = time.time()
            create_response = requests.post(
                f"{BASE_URL}/accounts",
                json=account_data,
                timeout=timeout
            )
            create_duration = time.time() - start_time

            # Sprawdzenie poprawności odpowiedzi
            assert create_response.status_code == 201, \
                f"Iteracja {i}: Nieprawidłowy status code przy tworzeniu: {create_response.status_code}"

            # Sprawdzenie czasu odpowiedzi
            assert create_duration < timeout, \
                f"Iteracja {i}: Tworzenie konta zajęło {create_duration:.3f}s (limit: {timeout}s)"

            # Pobranie ID utworzonego konta (w Twoim API to PESEL)
            account_id = create_response.json().get("id")
            assert account_id is not None, f"Iteracja {i}: Brak ID w odpowiedzi"
            assert account_id == pesel, f"Iteracja {i}: ID nie zgadza się z PESEL"

            # Usuwanie konta
            start_time = time.time()
            delete_response = requests.delete(
                f"{BASE_URL}/accounts/{account_id}",
                timeout=timeout
            )
            delete_duration = time.time() - start_time

            # Sprawdzenie poprawności odpowiedzi
            assert delete_response.status_code == 200, \
                f"Iteracja {i}: Nieprawidłowy status code przy usuwaniu: {delete_response.status_code}"

            # Sprawdzenie czasu odpowiedzi
            assert delete_duration < timeout, \
                f"Iteracja {i}: Usuwanie konta zajęło {delete_duration:.3f}s (limit: {timeout}s)"

    def test_account_with_100_incoming_transfers(self):
        timeout = 0.5
        initial_balance = 0  # W Twoim API nowe konto ma saldo 0
        deposit_amount = 50.0
        number_of_deposits = 100

        # Generuj unikalny PESEL
        pesel = "80000000000"

        # Tworzenie konta
        account_data = {
            "first_name": "Performance",
            "last_name": "Test",
            "pesel": pesel
        }

        start_time = time.time()
        create_response = requests.post(
            f"{BASE_URL}/accounts",
            json=account_data,
            timeout=timeout
        )
        create_duration = time.time() - start_time

        assert create_response.status_code == 201, \
            f"Nieprawidłowy status code przy tworzeniu konta: {create_response.status_code}"
        assert create_duration < timeout, \
            f"Tworzenie konta zajęło {create_duration:.3f}s (limit: {timeout}s)"

        account_id = create_response.json().get("id")
        assert account_id is not None, "Brak ID w odpowiedzi"

        # Wykonywanie wpłat (deposit)
        for i in range(number_of_deposits):
            deposit_data = {
                "amount": deposit_amount
            }

            start_time = time.time()
            deposit_response = requests.post(
                f"{BASE_URL}/accounts/{account_id}/deposit",
                json=deposit_data,
                timeout=timeout
            )
            deposit_duration = time.time() - start_time

            # Sprawdzenie poprawności odpowiedzi
            assert deposit_response.status_code == 200, \
                f"Wpłata {i}: Nieprawidłowy status code: {deposit_response.status_code}"

            # Sprawdzenie czasu odpowiedzi
            assert deposit_duration < timeout, \
                f"Wpłata {i}: Operacja zajęła {deposit_duration:.3f}s (limit: {timeout}s)"

        # Sprawdzenie końcowego salda
        start_time = time.time()
        balance_response = requests.get(
            f"{BASE_URL}/accounts/{account_id}",
            timeout=timeout
        )
        balance_duration = time.time() - start_time

        assert balance_response.status_code == 200, \
            f"Nieprawidłowy status code przy pobieraniu salda: {balance_response.status_code}"
        assert balance_duration < timeout, \
            f"Pobieranie salda zajęło {balance_duration:.3f}s (limit: {timeout}s)"

        # Sprawdzenie poprawności salda
        expected_balance = initial_balance + (deposit_amount * number_of_deposits)
        actual_balance = balance_response.json().get("balance")

        assert actual_balance == expected_balance, \
            f"Nieprawidłowe saldo. Oczekiwano: {expected_balance}, otrzymano: {actual_balance}"

        # Sprzątanie - usunięcie konta
        requests.delete(f"{BASE_URL}/accounts/{account_id}", timeout=timeout)


class TestBulkAccountOperations:
    """Dodatkowe testy dla chętnych - operacje masowe"""

    @pytest.mark.skip(reason="Test dla chętnych - może trwać długo")
    def test_create_1000_accounts_then_delete_all(self):
        timeout = 0.5
        number_of_accounts = 1000
        account_ids = []

        print(f"\nTworzenie {number_of_accounts} kont...")

        # Faza 1: Tworzenie wszystkich kont
        for i in range(number_of_accounts):
            # Generuj unikalny PESEL (11 cyfr)
            pesel = f"{85000000000 + i:011d}"

            account_data = {
                "first_name": f"Bulk{i}",
                "last_name": "Test",
                "pesel": pesel
            }

            start_time = time.time()
            response = requests.post(
                f"{BASE_URL}/accounts",
                json=account_data,
                timeout=timeout
            )
            duration = time.time() - start_time

            assert response.status_code == 201, \
                f"Konto {i}: Nieprawidłowy status code: {response.status_code}"
            assert duration < timeout, \
                f"Konto {i}: Tworzenie zajęło {duration:.3f}s (limit: {timeout}s)"

            account_id = response.json().get("id")
            assert account_id is not None, f"Konto {i}: Brak ID w odpowiedzi"
            account_ids.append(account_id)

            # Progress info co 100 kont
            if (i + 1) % 100 == 0:
                print(f"Utworzono {i + 1}/{number_of_accounts} kont")

        print(f"Wszystkie {number_of_accounts} kont utworzone. Rozpoczynam usuwanie...")

        # Faza 2: Usuwanie wszystkich kont
        for i, account_id in enumerate(account_ids):
            start_time = time.time()
            response = requests.delete(
                f"{BASE_URL}/accounts/{account_id}",
                timeout=timeout
            )
            duration = time.time() - start_time

            assert response.status_code == 200, \
                f"Konto {i} (ID: {account_id}): Nieprawidłowy status code: {response.status_code}"
            assert duration < timeout, \
                f"Konto {i} (ID: {account_id}): Usuwanie zajęło {duration:.3f}s (limit: {timeout}s)"

            # Progress info co 100 kont
            if (i + 1) % 100 == 0:
                print(f"Usunięto {i + 1}/{number_of_accounts} kont")

        print(f"Wszystkie {number_of_accounts} kont usunięte pomyślnie!")