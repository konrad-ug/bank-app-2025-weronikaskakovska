import os
import requests
from datetime import datetime


class BuisnessAccount:
    MF_API_URL = os.getenv('BANK_APP_MF_URL', 'https://wl-test.mf.gov.pl')
    def __init__(self, company_name, nip):
        self.company_name = company_name
        self.balance = 0
        self.history = []

        if len(nip) != 10:
            print(f"[WARNING] NIP has invalid length: {len(nip)} (expected 10)")
            self.nip = "Invalid"
            return

        if not self._validate_nip_in_mf(nip):
            raise ValueError("Company not registered!!")

        self.nip = nip

    def calculate_tax(self):
        return 0.19

    def _validate_nip_in_mf(self, nip):
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            url = f"{self.MF_API_URL}/api/search/nip/{nip}?date={today}"
            print(f"[INFO] Validating NIP {nip} at {url}")
            response = requests.get(url, timeout=10)
            print(f"[INFO] Response status: {response.status_code}")
            print(f"[INFO] Response body: {response.text}")

            if response.status_code != 200:
                print(f"[WARNING] API returned status {response.status_code}")
                return False

            data = response.json()

            if "result" in data and data["result"]:
                subject = data["result"].get("subject", {})
                status_vat = subject.get("statusVat", "")

                print(f"[INFO] VAT status: {status_vat}")

                return status_vat == "Czynny"

            print("[WARNING] No result in API response")
            return False

        except requests.RequestException as e:
            print(f"[ERROR] Request failed: {e}")
            return False
        except (KeyError, ValueError) as e:
            print(f"[ERROR] Failed to parse response: {e}")
            return False

    def deposit(self, amount):
        self.balance += amount
        self.history.append(amount)

    def withdraw(self, amount):
        if amount > self.balance:
            raise ValueError("Za mało środków")
        self.balance -= amount
        self.history.append(-amount)

    def express_transfer(self, amount):
        if amount > self.balance:
            raise ValueError("Brak środków")
        self.balance -= (amount + 5)
        self.history.append(-amount)
        self.history.append(-5)

    def take_loan(self, amount):
        has_enough_balance = self.balance >= 2 * amount
        has_zus_transfer = -1775 in self.history

        if has_enough_balance and has_zus_transfer:
            self.balance += amount
            self.history.append(amount)
            return True
        else:
            return False

