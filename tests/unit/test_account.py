import pytest
from account import Account, AccountsRegistry

class TestAccount:
    @pytest.fixture
    def valid_pesel(self):
        return "02270803628"

    @pytest.fixture
    def registry(self):
        return AccountsRegistry()

    @pytest.mark.parametrize("pesel, expected", [
        ("12345678910", "12345678910"),
        ("12345", "Invalid"),
        ("12345678901011", "Invalid"),
    ])
    def test_pesel(self, pesel, expected):
        account = Account("John", "Doe", pesel)
        assert account.pesel == expected

    def test_age_validation_invalid_pesel(self):
        account = Account("X", "Y", "12345")
        assert account.pesel == "Invalid"
        assert account._age_validation() is False

    @pytest.mark.parametrize("pesel, expected_valid", [
        ("50010112345", True),
        ("02210112345", True),
        ("02410112345", False),
        ("02610112345", False),
        ("80810112345", False),
    ])
    def test_age_validation_all_centuries(self, pesel, expected_valid):
        acc = Account("Test", "User", pesel)
        assert acc._age_validation() is expected_valid

    @pytest.mark.parametrize("promo, expected_balance", [
        ("PROM_ABC", 50),
        ("CODE_ABC", 0),
        (None, 0),
    ])

    def test_promo_code(self, valid_pesel, promo, expected_balance):
        acc = Account("Jan", "Kowalski", valid_pesel, promo_code=promo)
        assert acc.balance == expected_balance

    def test_promo_code_validation_true(self, valid_pesel):
        acc = Account("A", "B", valid_pesel)
        assert acc._promo_code_validation("PROM_X") is True

    def test_promo_code_validation_false_string(self, valid_pesel):
        acc = Account("A", "B", valid_pesel)
        assert acc._promo_code_validation("ABC") is False

    @pytest.mark.parametrize("pesel", [
        "99990803628",
    ])
    def test_age_validation_invalid_month(self, pesel):
        acc = Account("A", "B", pesel)
        assert acc._age_validation() is False

    @pytest.mark.parametrize("pesel", [
        "00210803628",  # 2000
        "00410803628",  # 2100
        "00610803628",  # 2200
        "00810803628",  # 1800
    ])
    def test_age_validation_all_centuries(self, valid_pesel, pesel):
        acc = Account("A", "B", pesel)
        assert acc._age_validation() in (True, False)

    def test_age_validation_before_1960(self):
        acc = Account("A", "B", "59010112345")
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

    def test_loan_condition2_false(self, valid_pesel):
        acc = Account("A", "B", valid_pesel)
        acc.history = [100, -50, 20]
        assert acc.loan_condition2(200) is False

    def test_loan_condition1_not_enough_history(self, valid_pesel):
        acc = Account("A", "B", valid_pesel)
        acc.history = [100, -20]
        assert acc.loan_condition1(1000) is False


    @pytest.mark.parametrize("number_of_accounts", [0, 1, 3, 5])
    def test_accounts_registry_count(self, registry, number_of_accounts):
        for i in range(number_of_accounts):
            registry.add_account(Account("Jan", "Test", f"9001011234{i}"))

        assert registry.count_accounts() == number_of_accounts

    def test_withdraw_history(self, valid_pesel):
        acc = Account("Test", "User", valid_pesel)
        acc.deposit(100)
        acc.withdraw(30)
        assert acc.history == [100, -30]

    def test_loan_condition2_insufficient_history(self, valid_pesel):
        acc = Account("Test", "User", valid_pesel)
        acc.history = [100, 50]
        assert acc.loan_condition2(100) is False

    def test_loan_condition2_with_negatives(self, valid_pesel):
        acc = Account("Test", "User", valid_pesel)
        acc.history = [100, -50, 200]
        assert acc.loan_condition2(100) is False

        acc.history = [100, 50, -20]
        assert acc.loan_condition2(100) is False

    def test_loan_condition2_returns_false(self, valid_pesel):
        acc = Account("Test", "User", valid_pesel)
        acc.history = [100, 50, 0]
        result = acc.loan_condition2(100)
        assert result is False

    def test_loan_condition1_exactly_5_items(self, valid_pesel):
        acc = Account("Test", "User", valid_pesel)
        acc.history = [50, 50, 50, 50, 50]
        assert acc.loan_condition1(200) is True
        assert acc.loan_condition1(300) is False

    def test_registry_find_by_pesel_not_found(self, registry, valid_pesel):
        acc = Account("Jan", "Kowalski", valid_pesel)
        registry.add_account(acc)

        result = registry.find_by_pesel("99999999999")
        assert result is None

    def test_registry_delete_nonexistent(self, registry):
        result = registry.delete_by_pesel("99999999999")
        assert result is False

    def test_registry_delete_existing(self, registry, valid_pesel):
        acc = Account("Jan", "Kowalski", valid_pesel)
        registry.add_account(acc)

        result = registry.delete_by_pesel(valid_pesel)
        assert result is True
        assert registry.count_accounts() == 0

    def test_registry_get_all_accounts(self, registry):
        acc1 = Account("Jan", "Kowalski", "90010112345")
        acc2 = Account("Anna", "Nowak", "92020212345")

        registry.add_account(acc1)
        registry.add_account(acc2)

        all_accounts = registry.get_all_accounts()
        assert len(all_accounts) == 2
        assert acc1 in all_accounts
        assert acc2 in all_accounts

    def test_account_equality(self):
        acc1 = Account("Jan", "Kowalski", "90010112345")
        acc2 = Account("Anna", "Nowak", "90010112345")
        acc3 = Account("Jan", "Kowalski", "92020212345")

        assert acc1 == acc2
        assert acc1 != acc3

    def test_account_equality_with_non_account(self, valid_pesel):
        acc = Account("Jan", "Kowalski", valid_pesel)
        assert acc != "not an account"
        assert acc != 123
        assert acc != None

    def test_age_validation_year_1960(self):

        acc = Account("Test", "User", "60010112345")

        assert acc._age_validation() is True

    def test_age_validation_year_1961(self):
        acc = Account("Test", "User", "61010112345")
        assert acc._age_validation() is True

    def test_submit_loan_condition2_true(self, valid_pesel):
        acc = Account("Test", "User", valid_pesel)
        acc.history = [100, 200, 300]
        result = acc.submit_for_loan(50)
        assert result is True
        assert acc.balance == 50
        assert 50 in acc.history

    def test_loan_balance_increase(self, valid_pesel):
        acc = Account("Test", "User", valid_pesel)
        acc.history = [100, 200, 300, 400, 500]
        acc.submit_for_loan(1000)
        assert acc.balance == 1000
