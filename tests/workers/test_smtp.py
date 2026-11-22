import smtplib
import ssl
from unittest.mock import MagicMock

import pytest

from src.notification.infrastructure.messaging.smtp.sender import SMTPConfig, SMTPSender

pytestmark = pytest.mark.anyio


@pytest.mark.security
async def test_smtp_sender_uses_tls_and_builds_email(monkeypatch):
    factory = MagicMock()
    monkeypatch.setattr(smtplib, "SMTP_SSL", factory)
    config = SMTPConfig(
        host="smtp.test",
        port=465,
        username="test-user",
        password="test-password",
        from_address="sender@example.com",
        timeout_seconds=2,
    )

    await SMTPSender(config).send("recipient@example.com", "Local subject", "Local message")

    factory.assert_called_once()
    options = factory.call_args.kwargs.copy()
    context = options.pop("context")
    assert isinstance(context, ssl.SSLContext)
    assert context.check_hostname
    assert context.verify_mode == ssl.CERT_REQUIRED
    assert options == {"host": "smtp.test", "port": 465, "timeout": 2}
    connection = factory.return_value.__enter__.return_value
    connection.login.assert_called_once_with("test-user", "test-password")
    connection.send_message.assert_called_once()
    (message,) = connection.send_message.call_args.args
    assert (message["From"], message["To"], message["Subject"]) == (
        "sender@example.com",
        "recipient@example.com",
        "Local subject",
    )
    assert message.get_content().strip() == "Local message"
    factory.return_value.__exit__.assert_called_once()
