import os
import requests
from datetime import datetime
from smtp.smtp import SMTPClient



class BuisnessAccount: # pragma: no cover
    MF_API_URL = os.getenv('BANK_APP_MF_URL', 'https://wl-test.mf.gov.pl')
    def __init__(self, company_name, nip):
        self.company_name = company_name
        self.balance = 0
        self.history = []

        if len(nip) != 10:
            self.nip = "Invalid"
            return
        self.nip = nip

        if not self._nip_validation():
            raise ValueError("Company not registered!!")

    def calculate_tax(self):
        return 0.19

    def _validate_nip_in_mf(self, nip: str) -> bool:
        try:
            response = requests.get(
                f"{self.MF_API_URL}/api/search/nip/{nip}?date=2026-02-01",
                timeout=5
            )

            if response.status_code != 200:
                return False

            data = response.json()
            result = data.get("result")

            if not result or not result.get("subject"):
                return False

            return result["subject"].get("statusVat") == "Czynny"

        except Exception:
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

    def _nip_validation(self) -> bool:
        return self._validate_nip_in_mf(self.nip)

    def send_history_via_email(self, email_address: str) -> bool:
        subject = f"Account Transfer History {datetime.now().strftime('%Y-%m-%d')}"
        text = f"Company account history: {self.history}"
        try:
            return SMTPClient.send(subject, text, email_address)
        except Exception:
            return False
