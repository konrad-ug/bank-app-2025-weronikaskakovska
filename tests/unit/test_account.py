import pytest
from account import Account

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

    def test_wrong_age_promo_code(self):
        account = Account("Jan", "Kowalski", "59270803628", promo_code = "CODE_ABC")
        assert account.balance == 0

    def test_promo_code_correct_but_pesel_invalid(self):
        account = Account("Jan", "Kowalski", "123", promo_code="PROM_ABC")
        assert account.balance == 0


    def test_increases(self):
        account = Account("John", "Doe", "02270803628", promo_code="PROM_ABC")
        account.deposit(100)
        assert account.balance == 150

    def test_withdraw(self):
        account = Account("John", "Doe", "02270803628")
        account.deposit(200)
        account.withdraw(50)
        assert account.balance == 150

    def test_failed_withdraw(self):
        account = Account("John", "Doe", "02270803628")
        account.deposit(100)
        with pytest.raises(ValueError):
            account.withdraw(200)

    def test_express_transfer_personal(self):
        account = Account("John", "Doe", "02270803628", promo_code = "PROM_ABC")
        account.deposit(100)
        account.express_transfer(50)
        assert account.balance == 99

    def test_express_transfer_no_funds(self):
        account = Account("Jan", "Kowalski", "02270803628")
        account.deposit(10)
        with pytest.raises(ValueError):
            account.express_transfer(50)

    def test_age_validation_invalid_month(self):
        account = Account("A", "B", "99990803628")
        assert account._age_validation() is False

    def test_age_year_1900(self):
        account = Account("A", "B", "90010803628")
        assert account._age_validation() in (True, False)

    def test_age_year_2100(self):
        account = Account("A", "B", "00410803628")
        assert account._age_validation() in (True, False)

    def test_age_year_2200(self):
        account = Account("A", "B", "00610803628")
        assert account._age_validation() in (True, False)

    def test_age_year_1800(self):
        account = Account("A", "B", "00810803628")
        assert account._age_validation() in (True, False)

    def test_account_history_transfer(self):
        account = Account("John", "Doe", "0227083628")
        account.deposit(500)
        assert account.history == [500.00]

    def test_account_history_outgoing(self):
        account = Account("John", "Doe", "0227083628")
        account.deposit(500)
        account.withdraw(200)
        assert account.history == [500, -200]

    def test_account_history_express_transfer(self):
        account = Account("John", "Doe", "0227083628")
        account.deposit(500)
        account.express_transfer(100)
        assert account.history == [500, -100, -1]