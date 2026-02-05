import pytest
from unittest.mock import patch, Mock
from buisness_account import BuisnessAccount

class TestBuisnessAccount:
    @pytest.fixture
    def valid_nip(self):
        return "1234567891"

    @pytest.mark.parametrize("nip, expected", [
        ("12345", "Invalid"),
        ("1234567891", "1234567891"),
    ])
    @patch('buisness_account.requests.get')
    def test_nip_validation(self, mock_get, nip, expected):
        if len(nip) == 10:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "result": {"subject": {"statusVat": "Czynny"}}
            }
            mock_response.text = '{"result": {"subject": {"statusVat": "Czynny"}}}'
            mock_get.return_value = mock_response

        acc = BuisnessAccount("Firma 1", nip)
        assert acc.nip == expected

    @patch('buisness_account.requests.get')
    def test_deposit(self, mock_get, valid_nip):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "result": {"subject": {"statusVat": "Czynny"}}
        }
        mock_response.text = '{"result": {"subject": {"statusVat": "Czynny"}}}'
        mock_get.return_value = mock_response

        acc = BuisnessAccount("Firma 1", valid_nip)
        acc.deposit(300)
        assert acc.balance == 300

    @patch('buisness_account.requests.get')
    def test_withdraw(self, mock_get, valid_nip):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "result": {"subject": {"statusVat": "Czynny"}}
        }
        mock_response.text = '{"result": {"subject": {"statusVat": "Czynny"}}}'
        mock_get.return_value = mock_response

        acc = BuisnessAccount("Firma 1", valid_nip)
        acc.deposit(1000)
        acc.withdraw(200)
        assert acc.balance == 800

    @patch('buisness_account.requests.get')
    def test_withdraw_no_funds(self, mock_get, valid_nip):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "result": {"subject": {"statusVat": "Czynny"}}
        }
        mock_response.text = '{"result": {"subject": {"statusVat": "Czynny"}}}'
        mock_get.return_value = mock_response

        acc = BuisnessAccount("Firma 1", valid_nip)
        with pytest.raises(ValueError):
            acc.withdraw(500)

    @patch('buisness_account.requests.get')
    @pytest.mark.parametrize("amount, expected", [
        (50, 945),
        (300, 695),
    ])
    def test_express_transfer(self, mock_get, valid_nip, amount, expected):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "result": {"subject": {"statusVat": "Czynny"}}
        }
        mock_response.text = '{"result": {"subject": {"statusVat": "Czynny"}}}'
        mock_get.return_value = mock_response

        acc = BuisnessAccount("Firma 1", valid_nip)
        acc.deposit(1000)
        acc.express_transfer(amount)
        assert acc.balance == expected

    @patch('buisness_account.requests.get')
    def test_express_transfer_insufficient_funds(self, mock_get, valid_nip):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "result": {"subject": {"statusVat": "Czynny"}}
        }
        mock_response.text = '{"result": {"subject": {"statusVat": "Czynny"}}}'
        mock_get.return_value = mock_response

        acc = BuisnessAccount("Firma 1", valid_nip)
        with pytest.raises(ValueError):
            acc.express_transfer(200)

    @patch('buisness_account.requests.get')
    def test_history_express(self, mock_get, valid_nip):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "result": {"subject": {"statusVat": "Czynny"}}
        }
        mock_response.text = '{"result": {"subject": {"statusVat": "Czynny"}}}'
        mock_get.return_value = mock_response

        acc = BuisnessAccount("Firma1", valid_nip)
        acc.deposit(1000)
        acc.express_transfer(300)
        assert acc.history == [1000, -300, -5]

    @pytest.fixture
    def business_account(self, mock_requests):
        return BuisnessAccount("Firma", "9001011234")

    @pytest.fixture(autouse=True)
    def mock_requests(self):
        with patch('buisness_account.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "result": {"subject": {"statusVat": "Czynny"}}
            }
            mock_response.text = '{"result": {"subject": {"statusVat": "Czynny"}}}'
            mock_get.return_value = mock_response
            yield mock_get

    @pytest.mark.parametrize(
        "balance,history,loan_amount,expected_result,expected_balance",
        [
            (10000, [-1775], 3000, True, 13000),

            (10000, [], 3000, False, 10000),

            (5000, [-1775], 3000, False, 5000),

            (6000, [-1775], 3000, True, 9000),

            (4000, [-1775], 3000, False, 4000),
        ]
    )
    def test_business_account_take_loan(
            self,
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

    def test_calculate_tax(monkeypatch):
        monkeypatch.setattr(BuisnessAccount, "_nip_validation", lambda self: True)
        acc = BuisnessAccount("Firma", "1234567891")  # company_name, nip
        assert acc.calculate_tax() == 0.19

    class TestFeature18NIPValidation:

        @patch('buisness_account.requests.get')
        def test_create_account_with_valid_nip(self, mock_get):
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "result": {
                    "subject": {
                        "statusVat": "Czynny"
                    }
                }
            }
            mock_response.text = '{"result": {"subject": {"statusVat": "Czynny"}}}'
            mock_get.return_value = mock_response

            account = BuisnessAccount("Test Firma Sp. z o.o.", "8461627563")

            assert account.nip == "8461627563"
            assert account.company_name == "Test Firma Sp. z o.o."
            assert account.balance == 0

            assert mock_get.called
            assert "8461627563" in mock_get.call_args[0][0]

        @patch('buisness_account.requests.get')
        def test_create_account_with_invalid_nip_raises_error(self, mock_get):
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "result": {
                    "subject": {
                        "statusVat": "Zwolniony"
                    }
                }
            }
            mock_response.text = '{"result": {"subject": {"statusVat": "Zwolniony"}}}'
            mock_get.return_value = mock_response

            with pytest.raises(ValueError) as exc_info:
                BuisnessAccount("Test Firma", "8461627563")

            assert "Company not registered!!" in str(exc_info.value)

        @patch('buisness_account.requests.get')
        def test_create_account_nip_not_found(self, mock_get):
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"result": None}
            mock_response.text = '{"result": null}'
            mock_get.return_value = mock_response

            with pytest.raises(ValueError) as exc_info:
                BuisnessAccount("Test Firma", "0000000000")

            assert "Company not registered!!" in str(exc_info.value)

        @patch('buisness_account.requests.get')
        def test_create_account_api_returns_404(self, mock_get):
            mock_response = Mock()
            mock_response.status_code = 404
            mock_response.text = 'Not Found'
            mock_get.return_value = mock_response

            with pytest.raises(ValueError):
                BuisnessAccount("Test Firma", "8461627563")

        def test_create_account_with_invalid_length_nip(self):
            account = BuisnessAccount("Test Firma", "123")

            assert account.nip == "Invalid"
            assert account.company_name == "Test Firma"
            assert account.balance == 0

        @patch('buisness_account.requests.get')
        def test_create_account_api_timeout(self, mock_get):
            import requests
            mock_get.side_effect = requests.Timeout("Connection timeout")

            with pytest.raises(ValueError):
                BuisnessAccount("Test Firma", "8461627563")

        @pytest.mark.parametrize("status_vat,should_succeed", [
            ("Czynny", True),
            ("Zwolniony", False),
            ("Niezarejestrowany", False),
            ("", False),
        ])
        @patch('buisness_account.requests.get')
        def test_various_vat_statuses(self, mock_get, status_vat, should_succeed):
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "result": {"subject": {"statusVat": status_vat}}
            }
            mock_response.text = f'{{"result": {{"subject": {{"statusVat": "{status_vat}"}}}}}}'
            mock_get.return_value = mock_response

            if should_succeed:
                account = BuisnessAccount("Test Firma", "8461627563")
                assert account is not None
            else:
                with pytest.raises(ValueError):
                    BuisnessAccount("Test Firma", "8461627563")

        @patch('buisness_account.requests.get')
        def test_validate_nip_uses_correct_date_format(self, mock_get):
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "result": {"subject": {"statusVat": "Czynny"}}
            }
            mock_response.text = '{"result": {"subject": {"statusVat": "Czynny"}}}'
            mock_get.return_value = mock_response

            BuisnessAccount("Test Firma", "8461627563")

            call_url = mock_get.call_args[0][0]
            assert "date=" in call_url

            import re
            date_match = re.search(r'date=(\d{4}-\d{2}-\d{2})', call_url)
            assert date_match is not None

        @patch('buisness_account.requests.get')
        def test_account_can_use_methods_after_creation(self, mock_get):
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "result": {"subject": {"statusVat": "Czynny"}}
            }
            mock_response.text = '{"result": {"subject": {"statusVat": "Czynny"}}}'
            mock_get.return_value = mock_response

            account = BuisnessAccount("Test Firma", "8461627563")

            account.deposit(1000)
            assert account.balance == 1000

            account.withdraw(300)
            assert account.balance == 700
