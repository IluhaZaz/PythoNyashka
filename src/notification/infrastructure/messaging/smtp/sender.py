import asyncio
import smtplib
import ssl
from email.message import EmailMessage

from pydantic import EmailStr, Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class SMTPConfig(BaseSettings):
    host: str = "localhost"
    port: int = Field(default=1025, ge=1, le=65535)
    username: str | None = None
    password: SecretStr | None = None
    from_address: EmailStr = "noreply@example.com"
    use_tls: bool = False
    start_tls: bool = False
    timeout_seconds: float = Field(default=10.0, gt=0)

    model_config = SettingsConfigDict(env_prefix="smtp_")

    @model_validator(mode="after")
    def validate_connection(self) -> "SMTPConfig":
        if self.use_tls and self.start_tls:
            raise ValueError("Choose SMTP_USE_TLS or SMTP_START_TLS, not both")
        if bool(self.username) != bool(self.password):
            raise ValueError("SMTP_USERNAME and SMTP_PASSWORD must be configured together")
        return self


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

        client: smtplib.SMTP
        if self.config.use_tls:
            client = smtplib.SMTP_SSL(
                host=self.config.host, port=self.config.port,
                timeout=self.config.timeout_seconds, context=ssl.create_default_context(),
            )
        else:
            client = smtplib.SMTP(
                host=self.config.host, port=self.config.port, timeout=self.config.timeout_seconds,
            )
        with client:
            if self.config.start_tls:
                client.starttls(context=ssl.create_default_context())
            if self.config.username and self.config.password:
                client.login(self.config.username, self.config.password.get_secret_value())
            client.send_message(message)
