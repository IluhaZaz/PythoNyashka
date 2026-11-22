import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, create_autospec

import pytest
from aiokafka import AIOKafkaProducer
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth import main as auth
from src.auth.infrastructure.messaging.kafka.publisher import NotificationPublisher
from src.infrastructure.messaging.kafka import producer as kafka_producer
from src.notification import main as notification
from src.notification.infrastructure.messaging.kafka.consumer import NotificationConsumer

pytestmark = pytest.mark.anyio


@pytest.fixture
def session_factory():
    session_maker = Mock(return_value=create_autospec(AsyncSession, instance=True))
    session_maker.kw = {"bind": SimpleNamespace(dispose=AsyncMock())}
    return session_maker


async def test_auth_lifespan_starts_producer_and_disposes_resources(monkeypatch, session_factory):
    producer = create_autospec(AIOKafkaProducer, instance=True)
    kafka_factory = Mock(return_value=producer)
    monkeypatch.setattr(kafka_producer, "AIOKafkaProducer", kafka_factory)
    monkeypatch.setattr(auth, "DBSession", session_factory)
    monkeypatch.setattr(auth.app.state, "notification_publisher", None, raising=False)
    monkeypatch.setenv("KAFKA_BOOTSTRAP_SERVERS", "kafka.test:9092")

    async with auth.app.router.lifespan_context(auth.app):
        producer.start.assert_awaited_once()
        assert isinstance(auth.app.state.notification_publisher, NotificationPublisher)

    assert kafka_factory.call_args.kwargs["bootstrap_servers"] == "kafka.test:9092"
    producer.stop.assert_awaited_once()
    session_factory.kw["bind"].dispose.assert_awaited_once()


async def test_notification_lifespan_cancels_worker_before_stopping_consumer(
    monkeypatch,
    session_factory,
):
    consumer = create_autospec(NotificationConsumer, instance=True)
    running = asyncio.Event()
    cancelled = asyncio.Event()

    async def wait_for_record():
        running.set()
        try:
            await asyncio.Future()
        finally:
            cancelled.set()

    async def stop_consumer():
        assert cancelled.is_set()

    consumer.run.side_effect = wait_for_record
    consumer.stop.side_effect = stop_consumer
    monkeypatch.setattr(notification, "NotificationConsumer", Mock(return_value=consumer))
    monkeypatch.setattr(notification, "DBSession", session_factory)
    monkeypatch.setattr(notification.app.state, "notification_consumer", None, raising=False)
    monkeypatch.setenv("KAFKA_BOOTSTRAP_SERVERS", "kafka.test:9092")
    monkeypatch.setenv("SMTP_HOST", "smtp.test")
    monkeypatch.setenv("SMTP_PORT", "465")
    monkeypatch.setenv("SMTP_USERNAME", "test-user")
    monkeypatch.setenv("SMTP_PASSWORD", "test-password")
    monkeypatch.setenv("SMTP_FROM_ADDRESS", "noreply@example.com")
    monkeypatch.setenv("SMTP_TIMEOUT_SECONDS", "2")

    async with notification.app.router.lifespan_context(notification.app):
        await asyncio.wait_for(running.wait(), timeout=3)
        consumer.start.assert_awaited_once()
        assert notification.app.state.notification_consumer is consumer

    consumer.stop.assert_awaited_once()
    session_factory.kw["bind"].dispose.assert_awaited_once()
