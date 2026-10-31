import asyncio
import smtplib
import ssl
from email.message import EmailMessage

from pydantic import EmailStr, Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class SMTPConfig(BaseSettings):
    host: str = "localhost"
    port: int = Field(default=465, ge=1, le=65535)
    username: str
    password: SecretStr
    from_address: EmailStr = "noreply@example.com"
    timeout_seconds: float = Field(default=10.0, gt=0)

    model_config = SettingsConfigDict(env_prefix="smtp_")


class SMTPSender:
    def __init__(self, config: SMTPConfig) -> None:
        self.config = config

    async def send(self, recipient: str, subject: str, text: str) -> None:
        await asyncio.to_thread(self._send, recipient, subject, text)

    def _send(self, recipient: str, subject: str, text: str) -> None:
        message = EmailMessage()
        message["From"] = str(self.config.from_address)
        message["To"] = recipient
        message["Subject"] = subject
        message.set_content(text)

        with smtplib.SMTP_SSL(
            host=self.config.host, port=self.config.port,
            timeout=self.config.timeout_seconds, context=ssl.create_default_context(),
        ) as client:
            client.login(self.config.username, self.config.password.get_secret_value())
            client.send_message(message)
