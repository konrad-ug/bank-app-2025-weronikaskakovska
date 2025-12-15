import pytest
from buisness_account import BuisnessAccount

class TestBuisnessAccount:
    @pytest.fixture
    def valid_nip(self):
        return "1234567891"

    @pytest.mark.parametrize("nip, expected", [
        ("12345", "Invalid"),
        ("1234567891", "1234567891"),
    ])
    def test_nip_validation(self, nip, expected):
        acc = BuisnessAccount("Firma 1", nip)
        assert acc.nip == expected

    def test_deposit(self, valid_nip):
        acc = BuisnessAccount("Firma 1", valid_nip)
        acc.deposit(300)
        assert acc.balance == 300

    def test_withdraw(self, valid_nip):
        acc = BuisnessAccount("Firma 1", valid_nip)
        acc.deposit(1000)
        acc.withdraw(200)
        assert acc.balance == 800

    def test_withdraw_no_funds(self, valid_nip):
        acc = BuisnessAccount("Firma 1", valid_nip)
        with pytest.raises(ValueError):
            acc.withdraw(500)

    @pytest.mark.parametrize("amount, expected", [
        (50, 945),
        (300, 695),
    ])
    def test_express_transfer(self, valid_nip, amount, expected):
        acc = BuisnessAccount("Firma 1", valid_nip)
        acc.deposit(1000)
        acc.express_transfer(amount)
        assert acc.balance == expected

    def test_express_transfer_insufficient_funds(self, valid_nip):
        acc = BuisnessAccount("Firma 1", valid_nip)
        with pytest.raises(ValueError):
            acc.express_transfer(200)

    def test_history_express(self, valid_nip):
        acc = BuisnessAccount("Firma1", valid_nip)
        acc.deposit(1000)
        acc.express_transfer(300)
        assert acc.history == [1000, -300, -5]

    @pytest.fixture
    def business_account(self):
        return BuisnessAccount("Firma", "90010112345")

    @pytest.mark.parametrize(
        "balance,history,loan_amount,expected_result,expected_balance",
        [
            # OK: saldo >= 2x kredyt + ZUS
            (10000, [-1775], 3000, True, 13000),

            # brak ZUS
            (10000, [], 3000, False, 10000),

            # za małe saldo
            (5000, [-1775], 3000, False, 5000),

            # dokładnie 2x → OK
            (6000, [-1775], 3000, True, 9000),

            # tylko ZUS, za małe saldo
            (4000, [-1775], 3000, False, 4000),
        ]

    )

    def test_business_account_take_loan(
            business_account,
            balance,
            history,
            loan_amount,
            expected_result,
            expected_balance
    ):
        business_account.deposit(balance)

        for h in history:
            business_account.history.append(h)

        result = business_account.take_loan(loan_amount)

        assert result is expected_result
        assert business_account.balance == expected_balance


