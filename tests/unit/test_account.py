from src.account import Account


class TestAccount:
    def test_account_creation(self):
        account = Account("John", "Doe", "12345678910")
        assert account.first_name == "John"
        assert account.last_name == "Doe"
        assert account.balance == 0
        assert account.pesel == "12345678910"

    def test_pesel_too_short(self):
        account = Account("Jane", "Doe", "12345")
        assert account.pesel == "Invalid"

    def test_pesel_too_long(self):
        account = Account("Jane", "Doe", "12345678901011")
        assert account.pesel == "Invalid"

    def test_promo_code(self):
        account = Account("Jan", "Kowalski", "02270803628", promo_code = "PROM_ABC")
        assert account.balance == 50

    def test_wrong_promo_code(self):
        account = Account("Jan", "Kowalski", "12345678910", promo_code = "CODE_ABC")
        assert account.balance == 0

    def test_no_promo_code(self):
        account = Account("Jan", "Kowalski", "12345678910")
        assert account.balance == 0

    def test_correct_age_promo_code(self):
        account = Account("Jan", "Kowalski", "02270803628", promo_code = "PROM_ABC")
        assert account.balance == 50

    def test_wrong_age_promo_code(self):
        account = Account("Jan", "Kowalski", "59270803628", promo_code = "CODE_ABC")
        assert account.balance == 0
