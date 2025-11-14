import pytest
from buisness_account import BuisnessAccount

class TestBuisnessAccount:

    def test_invalid_nip(self):
        account = BuisnessAccount("Firma 1", "12345")
        assert account.nip == "Invalid"

    def test_valid_nip(self):
        account = BuisnessAccount("Firma 1", "1234567891")
        assert account.nip == "1234567891"

    def test_deposit(self):
        account = BuisnessAccount("Firma 1", "1234567891")
        account.deposit(300)
        assert account.balance == 300

    def test_withdraw(self):
        account = BuisnessAccount("Firma 1", "1234567891")
        account.deposit(1000)
        account.withdraw(200)
        assert account.balance == 800

    def test_withdraw_no_funds(self):
        account = BuisnessAccount("Firma 1", "1234567891")
        with pytest.raises(ValueError):
            account.withdraw(500)

    def test_express_transfer_buisness(self):
        account = BuisnessAccount("Firma 1", "1234567891")
        account.deposit(100)
        account.express_transfer(50)
        assert account.balance == 45

    def test_express_transfer_insufficient_funds(self):
        account = BuisnessAccount("Firma 1", "1234567891")
        with pytest.raises(ValueError):
            account.express_transfer(200)

    def test_buisness_account_history_express_transfer(self):
        account = BuisnessAccount("Firma1", "1234567891")
        account.deposit(1000)
        account.express_transfer(300)
        assert account.history == [1000, -300, -5]
