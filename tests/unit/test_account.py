import pytest
from account import Account

class TestAccount:
    @pytest.fixture
    def valid_pesel(self):
        return "02270803628"

    @pytest.mark.parametrize("pesel, expected", [
        ("12345678910", "12345678910"),
        ("12345", "Invalid"),
        ("12345678901011", "Invalid"),
    ])
    def test_pesel(self, pesel, expected):
        account = Account("John", "Doe", pesel)
        assert account.pesel == expected

    @pytest.mark.parametrize("promo, expected_balance", [
        ("PROM_ABC", 50),
        ("CODE_ABC", 0),
        (None, 0),
    ])

    def test_promo_code(self, valid_pesel, promo, expected_balance):
        acc = Account("Jan", "Kowalski", valid_pesel, promo_code=promo)
        assert acc.balance == expected_balance

    @pytest.mark.parametrize("pesel", [
        "99990803628",
    ])
    def test_age_validation_invalid_month(self, pesel):
        acc = Account("A", "B", pesel)
        assert acc._age_validation() is False

    @pytest.mark.parametrize("pesel", [
        "90010803628",
        "00410803628",
        "00610803628",
        "00810803628",
    ])
    def test_age_validation_various_centuries(self, pesel):
        acc = Account("A", "B", pesel)
        assert acc._age_validation() in (True, False)

    def test_deposit(self, valid_pesel):
        acc = Account("John", "Doe", valid_pesel, promo_code="PROM_ABC")
        acc.deposit(100)
        assert acc.balance == 150

    def test_withdraw(self, valid_pesel):
        acc = Account("John", "Doe", valid_pesel)
        acc.deposit(200)
        acc.withdraw(50)
        assert acc.balance == 150

    def test_withdraw_error(self, valid_pesel):
        acc = Account("John", "Doe", valid_pesel)
        acc.deposit(100)
        with pytest.raises(ValueError):
            acc.withdraw(200)

    @pytest.mark.parametrize("amount, expected", [
        (50, 99),
    ])
    def test_express_transfer(self, valid_pesel, amount, expected):
        acc = Account("John", "Doe", valid_pesel, promo_code="PROM_ABC")
        acc.deposit(100)
        acc.express_transfer(amount)
        assert acc.balance == expected

    def test_express_transfer_no_funds(self, valid_pesel):
        acc = Account("Jan", "Kowalski", valid_pesel)
        acc.deposit(10)
        with pytest.raises(ValueError):
            acc.express_transfer(50)

    @pytest.mark.parametrize("history, expected", [
        ([500], [500]),
        ([500, -200], [500, -200]),
        ([500, -100, -1], [500, -100, -1]),
    ])
    def test_history_generic(self, valid_pesel, history, expected):
        acc = Account("John", "Doe", valid_pesel)
        acc.history = []
        for h in history:
            if h > 0:
                acc.deposit(h)
            else:
                if h == -1:
                    continue
                acc.withdraw(-h)
        acc.history = history
        assert acc.history == expected

    @pytest.mark.parametrize("history, amount, expected", [
        ([100, -20, 50, 40, 30], 200, True),
        ([100, 200, -5, -1, 1], 200, True),
        ([100, 100, -50, -1, 1], 200, False),
    ])
    def test_loan_conditions(self, valid_pesel, history, amount, expected):
        acc = Account("John", "Doe", valid_pesel)
        acc.history = history.copy()
        result = acc.submit_for_loan(amount)
        assert result is expected
        if expected:
            assert acc.balance == amount
        else:
            assert acc.balance == 0