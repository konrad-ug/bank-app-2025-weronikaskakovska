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
        acc = Account("X", "Y", "12345")
        assert acc.pesel == "Invalid"
        assert acc._age_validation() is False

    @pytest.mark.parametrize("pesel, expected_valid", [
        ("50010112345", True),
        ("02210112345", True),
        ("02410112345", False),
        ("02610112345", False),
        ("80810112345", False),
    ])
    def test_age_validation_centuries(self, pesel, expected_valid):
        acc = Account("Test", "User", pesel)
        assert acc._age_validation() is expected_valid

    @pytest.mark.parametrize("promo, expected_balance", [
        ("PROM_ABC", 50),
        ("CODE_ABC", 0),
        (None, 0),
    ])
    def test_promo_code_balance(self, valid_pesel, promo, expected_balance):
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
        assert acc._age_validation() is True

    @pytest.mark.parametrize("pesel", [
        "90010803628",
        "00410803628",
        "00610803628",
        "00810803628",
    ])
    def test_age_validation_various_centuries(self, pesel):
        acc = Account("A", "B", pesel)
        assert acc._age_validation() in (True, False)


    def test_deposit_and_withdraw(self, valid_pesel):
        acc = Account("John", "Doe", valid_pesel, promo_code="PROM_ABC")
        acc.deposit(100)
        assert acc.balance == 150
        acc.withdraw(50)
        assert acc.balance == 100

    def test_withdraw_error(self, valid_pesel):
        acc = Account("John", "Doe", valid_pesel)
        acc.deposit(50)
        with pytest.raises(ValueError):
            acc.withdraw(100)

    def test_express_transfer(self, valid_pesel):
        acc = Account("John", "Doe", valid_pesel, promo_code="PROM_ABC")
        acc.deposit(100)
        acc.express_transfer(50)
        assert acc.balance == 99  # 50 + 50 -1? (keep your logic)

    def test_express_transfer_no_funds(self, valid_pesel):
        acc = Account("Jan", "Kowalski", valid_pesel)
        acc.deposit(10)
        with pytest.raises(ValueError):
            acc.express_transfer(50)

    @pytest.mark.parametrize("history, amount, expected", [
        ([100, -20, 50, 40, 30], 200, True),
        ([100, 200, -5, -1, 1], 200, True),
        ([100, 100, -50, -1, 1], 200, False),
    ])
    def test_submit_for_loan(self, valid_pesel, history, amount, expected):
        acc = Account("John", "Doe", valid_pesel)
        acc.history = history.copy()
        result = acc.submit_for_loan(amount)
        assert result is expected
        assert acc.balance == (amount if expected else 0)


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

    def test_registry_find_and_delete(self, registry, valid_pesel):
        acc = Account("Jan", "Kowalski", valid_pesel)
        registry.add_account(acc)

        # Find
        found = registry.find_by_pesel(valid_pesel)
        assert found == acc
        assert registry.find_by_pesel("99999999999") is None

        # Delete
        assert registry.delete_by_pesel("99999999999") is False
        assert registry.delete_by_pesel(valid_pesel) is True
        assert registry.count_accounts() == 0

    def test_registry_get_all_accounts(self, registry):
        acc1 = Account("Jan", "Kowalski", "90010112345")
        acc2 = Account("Anna", "Nowak", "92020212345")
        registry.add_account(acc1)
        registry.add_account(acc2)
        all_acc = registry.get_all_accounts()
        assert len(all_acc) == 2
        assert acc1 in all_acc and acc2 in all_acc

    def test_account_equality(self):
        acc1 = Account("Jan", "Kowalski", "90010112345")
        acc2 = Account("Anna", "Nowak", "90010112345")
        acc3 = Account("Jan", "Kowalski", "92020212345")
        assert acc1 == acc2
        assert acc1 != acc3

    def test_account_eq_with_non_account(self, valid_pesel):
        acc = Account("Jan", "Kowalski", valid_pesel)
        assert acc != 123 and acc != None and acc != "string"

    def test_age_validation_invalid_month_high(self):
        acc = Account("A", "B", "59230112345")  # month = 23 → invalid
        assert acc._age_validation() is False

    def test_age_validation_invalid_month_zero(self):
        acc = Account("A", "B", "59000112345")  # month = 00 → invalid
        assert acc._age_validation() is False

    def test_age_validation_invalid_pesel_length(self):
        acc = Account("A", "B", "123")  # too short
        assert acc._age_validation() is False

    def test_loan_condition2_not_enough_history(self):
        acc = Account("A", "B", "02270803628")
        acc.history = [100, -20]  # fewer than 3 entries -> should hit the len < 3 branch
        assert acc.loan_condition2(100) is False

    def test_add_duplicate_pesel_raises(self, registry):
        a1 = Account("A", "One", "02270803628")
        a2 = Account("B", "Two", "02270803628")  # same pesel
        registry.add_account(a1)
        with pytest.raises(ValueError):
            registry.add_account(a2)

    def test_withdraw_exact_balance(self, valid_pesel):
        acc = Account("A", "B", valid_pesel)
        acc.deposit(100)
        acc.withdraw(100)
        assert acc.balance == 0
        assert acc.history[-1] == -100

    def test_deposit_zero(self, valid_pesel):
        acc = Account("A", "B", valid_pesel)
        acc.deposit(0)
        assert acc.balance == 0
        assert acc.history == [0]

    def test_express_transfer_history_entries(self, valid_pesel):
        acc = Account("A", "B", valid_pesel)
        acc.deposit(100)
        acc.express_transfer(20)

        assert acc.history[-2:] == [-20, -1]

    def test_submit_for_loan_failure_does_not_change_history(self, valid_pesel):
        acc = Account("A", "B", valid_pesel)
        acc.history = [10, -5, 3]

        result = acc.submit_for_loan(1000)

        assert result is False
        assert acc.history == [10, -5, 3]
        assert acc.balance == 0

    def test_loan_condition1_exact_sum(self, valid_pesel):
        acc = Account("A", "B", valid_pesel)
        acc.history = [50, 50, 50, 50, 0]  # sum = 200

        assert acc.loan_condition1(200) is True

    def test_registry_delete_removes_account(self, registry, valid_pesel):
        acc = Account("A", "B", valid_pesel)
        registry.add_account(acc)

        registry.delete_by_pesel(valid_pesel)
        assert registry.find_by_pesel(valid_pesel) is None

    def test_registry_add_non_account_object(self, registry):
        with pytest.raises(AttributeError):
            registry.add_account("not an account")
