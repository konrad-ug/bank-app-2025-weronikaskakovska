from src.buisness_account import BuisnessAccount

class TestBuisnessAccount:

    def test_invalid_nip(self):
        account = BuisnessAccount("Firma 1", "12345")
        assert account.nip == "Invalid"

    def test_valid_nip(self):
        account = BuisnessAccount("Firma 1", "1234567891")
        assert account.nip == "1234567891"

    def test_withdraw(self):
        account = BuisnessAccount("Firma 1", "1234567891")
        account.deposit(1000)
        account.withdraw(200)
        assert account.balance == 800

    def test_express_transfer_buisness(self):
        account = BuisnessAccount("Firma 1", "1234567891")
        account.deposit(100)
        account.express_transfer(50)
        assert account.balance == 45
