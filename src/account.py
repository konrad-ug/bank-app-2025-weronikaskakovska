class Account:
    def __init__(self, first_name, last_name, pesel, promo_code = None):
        self.first_name = first_name
        self.last_name = last_name
        self.history = []

        if len(pesel) == 11:
            self.pesel = pesel
        else:
            self.pesel = "Invalid"

        self.balance = 0

        if self._promo_code_validation(promo_code) and self._age_validation():
            self.balance += 50

    def __eq__(self, other):
        if not isinstance(other, Account):
            return False
        return self.pesel == other.pesel

    def _promo_code_validation(self, promo_code):
        if promo_code is None:
            return False
        else:
            return promo_code.startswith("PROM_")

    def _age_validation(self):
        if self.pesel == "Invalid":
            return False

        year = int(self.pesel[0:2])
        month = int(self.pesel[2:4])

        if 1 <= month <= 12:
            year += 1900
        elif 21 <= month <= 32:
            year += 2000
        elif 41 <= month <= 52:
            year += 2100
        elif 61 <= month <= 72:
            year += 2200
        elif 81 <= month <= 92:
            year += 1800
        else:
            return False

        current_year = 2026
        return 1950 <= year <= current_year

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
            raise ValueError("Brak środkow")
        self.balance -= (amount + 1)
        self.history.append(-amount)
        self.history.append(-1)

    def submit_for_loan(self, amount):
        if self.loan_condition1(amount) or self.loan_condition2(amount):
            self.balance += amount
            self.history.append(amount)
            return True
        else:
            return False

    def loan_condition1(self, amount):
        if len(self.history) >= 5:
            return sum(self.history[-5:]) >= amount
        else:
            return False

    def loan_condition2(self, amount):
        if len(self.history) < 3:
            return False
        return self.history[-1] > 0 and self.history[-2] > 0 and self.history[-3] > 0


class AccountsRegistry:
    def __init__(self):
        self.accounts = []

    def add_account(self, account):
        self.accounts.append(account)

    def find_by_pesel(self, pesel):
        for account in self.accounts:
            if account.pesel == pesel:
                return account
        return None

    def delete_by_pesel(self, pesel):
        account = self.find_by_pesel(pesel)
        if account is None:
            return False

        self.accounts = [acc for acc in self.accounts if acc.pesel != pesel]
        return True

    def get_all_accounts(self):
        return self.accounts

    def count_accounts(self):
        return len(self.accounts)