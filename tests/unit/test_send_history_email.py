import pytest
from datetime import datetime
from unittest.mock import Mock

try:
    from account import Account
    from buisness_account import BuisnessAccount
    import smtp.smtp as smtpmod
except Exception:
    from account import Account
    from buisness_account import BuisnessAccount
    import smtp.smtp as smtpmod


def test_personal_send_history_success(monkeypatch):
    acc = Account("Jan", "Kowalski", "02270803628")
    acc.history = [100, -1, 500]

    mock_send = Mock(return_value=True)
    monkeypatch.setattr(smtpmod.SMTPClient, "send", mock_send)

    email = "person@example.com"
    res = acc.send_history_via_email(email)
    assert res is True

    today = datetime.now().strftime("%Y-%m-%d")
    expected_subject = f"Account Transfer History {today}"
    expected_text = f"Personal account history: {acc.history}"
    mock_send.assert_called_once_with(expected_subject, expected_text, email)


def test_personal_send_history_failure(monkeypatch):
    acc = Account("Jan", "Kowalski", "02270803628")
    acc.history = [10, -5]

    mock_send = Mock(return_value=False)
    monkeypatch.setattr(smtpmod.SMTPClient, "send", mock_send)

    email = "person2@example.com"
    res = acc.send_history_via_email(email)
    assert res is False

    today = datetime.now().strftime("%Y-%m-%d")
    expected_subject = f"Account Transfer History {today}"
    expected_text = f"Personal account history: {acc.history}"
    mock_send.assert_called_once_with(expected_subject, expected_text, email)


def test_business_send_history_success(monkeypatch):
    monkeypatch.setattr(BuisnessAccount, "_nip_validation", lambda self: True)

    acc = BuisnessAccount("Firma", "1234567891")
    acc.history = [5000, -1000, 500]

    mock_send = Mock(return_value=True)
    monkeypatch.setattr(smtpmod.SMTPClient, "send", mock_send)

    email = "company@example.com"
    res = acc.send_history_via_email(email)
    assert res is True

    today = datetime.now().strftime("%Y-%m-%d")
    expected_subject = f"Account Transfer History {today}"
    expected_text = f"Company account history: {acc.history}"
    mock_send.assert_called_once_with(expected_subject, expected_text, email)


def test_business_send_history_failure(monkeypatch):
    monkeypatch.setattr(BuisnessAccount, "_nip_validation", lambda self: True)

    acc = BuisnessAccount("Firma", "1234567891")
    acc.history = [1]

    mock_send = Mock(return_value=False)
    monkeypatch.setattr(smtpmod.SMTPClient, "send", mock_send)

    email = "company2@example.com"
    res = acc.send_history_via_email(email)
    assert res is False

    today = datetime.now().strftime("%Y-%m-%d")
    expected_subject = f"Account Transfer History {today}"
    expected_text = f"Company account history: {acc.history}"
    mock_send.assert_called_once_with(expected_subject, expected_text, email)