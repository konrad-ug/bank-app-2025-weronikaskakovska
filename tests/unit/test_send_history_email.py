import pytest
import builtins
import importlib
import sys
from datetime import datetime
from unittest.mock import Mock
from smtp.smtp import SMTPClient
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


def test_smtp_send_returns_false():
    result = SMTPClient.send("Test subject", "Test text", "a@b.com")
    assert result is False

def test_personal_send_history_smtp_exception(monkeypatch):
    acc = Account("A", "B", "02270803628")
    acc.history = [10, 20]

    def raise_exc(*args, **kwargs):
        raise RuntimeError("fail")

    monkeypatch.setattr(smtpmod.SMTPClient, "send", raise_exc)
    result = acc.send_history_via_email("test@example.com")
    assert result is False

def test_business_send_history_smtp_exception(monkeypatch):
    monkeypatch.setattr(BuisnessAccount, "_nip_validation", lambda self: True)
    acc = BuisnessAccount("Firma", "1234567891")
    acc.history = [10, 20]

    def raise_exc(*args, **kwargs):
        raise RuntimeError("fail")

    monkeypatch.setattr(smtpmod.SMTPClient, "send", raise_exc)
    result = acc.send_history_via_email("test@example.com")
    assert result is False


def test_smtp_client_init():
    client = SMTPClient()
    assert client is not None


def test_send_history_empty(monkeypatch):
    acc = Account("A","B","1")
    mock_send = Mock(return_value=True)
    monkeypatch.setattr(smtpmod.SMTPClient, "send", mock_send)
    result = acc.send_history_via_email("a@b.com")
    assert result is True